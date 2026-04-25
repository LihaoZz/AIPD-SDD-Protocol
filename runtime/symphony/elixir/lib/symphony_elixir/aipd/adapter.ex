defmodule SymphonyElixir.Aipd.Adapter do
  @moduledoc """
  File-backed AIPD Mission Block tracker adapter.
  """

  @behaviour SymphonyElixir.Tracker

  alias SymphonyElixir.Aipd.GateOutcome
  alias SymphonyElixir.Config
  alias SymphonyElixir.Linear.Issue

  @active_states ["ready", "failed", "blocked"]
  @terminal_states ["done", "closed"]
  @finish_actions [
    "defer_retry",
    "schedule_semantic_retry",
    "release_and_pause",
    "release_and_wait_input",
    "pause_wait_human",
    "release_to_review",
    "close_mb",
    "stop_and_route_owner",
    "stop_and_route_recovery"
  ]

  @spec fetch_candidate_issues() :: {:ok, [Issue.t()]} | {:error, term()}
  def fetch_candidate_issues do
    with {:ok, root} <- aipd_root() do
      {:ok,
       root
       |> machine_spec_paths()
       |> Enum.flat_map(&issue_from_machine_spec(root, &1))
       |> Enum.reject(&terminal_issue?/1)
       |> Enum.reject(&blocked_dependency?(root, &1))}
    end
  end

  @spec fetch_issues_by_states([String.t()]) :: {:ok, [Issue.t()]} | {:error, term()}
  def fetch_issues_by_states(states) do
    normalized = MapSet.new(Enum.map(states, &normalize_state/1))

    with {:ok, issues} <- fetch_candidate_issues() do
      {:ok, Enum.filter(issues, fn %Issue{state: state} -> MapSet.member?(normalized, normalize_state(state)) end)}
    end
  end

  @spec fetch_issue_states_by_ids([String.t()]) :: {:ok, [Issue.t()]} | {:error, term()}
  def fetch_issue_states_by_ids(issue_ids) do
    wanted = MapSet.new(issue_ids)

    with {:ok, root} <- aipd_root() do
      issues =
        root
        |> machine_spec_paths()
        |> Enum.flat_map(&issue_from_machine_spec(root, &1))
        |> Enum.filter(fn %Issue{id: id} -> MapSet.member?(wanted, id) end)

      {:ok, issues}
    end
  end

  @spec create_comment(String.t(), String.t()) :: :ok | {:error, term()}
  def create_comment(issue_id, body) do
    with {:ok, root} <- aipd_root() do
      dir = Path.join([root, "runtime", "symphony", "comments"])
      File.mkdir_p!(dir)
      File.write(Path.join(dir, "#{safe_name(issue_id)}.txt"), body <> "\n", [:append])
    end
  end

  @spec update_issue_state(String.t(), String.t()) :: :ok | {:error, term()}
  def update_issue_state(issue_id, state_name) do
    with {:ok, root} <- aipd_root() do
      dir = Path.join([root, "runtime", "symphony", "state_updates"])
      File.mkdir_p!(dir)
      payload = Jason.encode!(%{"mb_id" => issue_id, "state" => state_name, "recorded_at" => DateTime.utc_now()})
      File.write(Path.join(dir, "#{safe_name(issue_id)}.jsonl"), payload <> "\n", [:append])
    end
  end

  @spec claim_issue(Issue.t()) :: :ok | {:error, term()}
  def claim_issue(%Issue{id: mb_id}) when is_binary(mb_id) do
    with {:ok, root} <- aipd_root(),
         :ok <- ensure_start_gate(root, mb_id),
         {:ok, outcome} <- GateOutcome.load(start_gate_path(root, mb_id)),
         :ok <- require_action(outcome, "dispatch_codex"),
         :ok <- require_may_start(outcome) do
      :ok
    end
  end

  def claim_issue(_), do: {:error, :invalid_aipd_issue}

  @spec finish_issue(Issue.t(), String.t() | nil, String.t() | nil) :: :ok | {:error, term()}
  def finish_issue(%Issue{id: mb_id}, workspace_root, summary)
      when is_binary(mb_id) and is_binary(workspace_root) do
    with {:ok, root} <- aipd_root(),
         :ok <- ensure_finish_gate(root, workspace_root, mb_id, summary),
         {:ok, outcome} <- GateOutcome.load(finish_gate_path(root, mb_id)),
         :ok <- require_finish_action(outcome) do
      :ok
    end
  end

  def finish_issue(%Issue{}, nil, _summary), do: {:error, :missing_workspace_root}
  def finish_issue(_, _, _), do: {:error, :invalid_aipd_issue}

  @spec aipd_tracker?() :: boolean()
  def aipd_tracker?, do: Config.settings!().tracker.kind == "aipd_mb"

  defp aipd_root do
    case Config.settings!().tracker.aipd_root do
      root when is_binary(root) and root != "" -> {:ok, Path.expand(root)}
      _ -> {:error, :missing_aipd_root}
    end
  end

  defp machine_spec_paths(root) do
    root
    |> Path.join("missions/*.machine.json")
    |> Path.wildcard()
    |> Enum.sort()
  end

  defp issue_from_machine_spec(root, path) do
    with {:ok, body} <- File.read(path),
         {:ok, spec} <- Jason.decode(body),
         mb_id when is_binary(mb_id) <- Map.get(spec, "mb_id"),
         true <- File.exists?(Path.join([root, "missions", "#{mb_id}.md"])) do
      state = runtime_state(root, mb_id)

      [
        %Issue{
          id: mb_id,
          identifier: mb_id,
          title: Map.get(spec, "goal", mb_id),
          description: description(spec, state),
          priority: Map.get(spec, "priority"),
          state: mapped_state(state),
          branch_name: mb_id,
          url: "aipd://#{mb_id}",
          blocked_by: get_in(spec, ["concurrency", "blocked_by_mbs"]) || [],
          labels: ["aipd_mb"],
          assigned_to_worker: true,
          updated_at: DateTime.utc_now()
        }
      ]
    else
      _ -> []
    end
  end

  defp runtime_state(root, mb_id) do
    path = Path.join([root, "runtime", "state", "#{mb_id}.state.json"])

    with {:ok, body} <- File.read(path),
         {:ok, state} <- Jason.decode(body) do
      state
    else
      _ -> %{"status" => "ready", "review_required" => false}
    end
  end

  defp mapped_state(%{"status" => "passed", "review_required" => true}), do: "review"
  defp mapped_state(%{"status" => "passed"}), do: "done"
  defp mapped_state(%{"status" => status}) when status in ["running", "verifying"], do: "in_progress"
  defp mapped_state(%{"status" => "failed"}), do: "retry_waiting"
  defp mapped_state(%{"status" => status}) when status in ["blocked", "routed_to_recovery"], do: "blocked"
  defp mapped_state(%{"status" => status}) when is_binary(status), do: status
  defp mapped_state(_), do: "ready"

  defp description(spec, state) do
    Jason.encode!(%{
      "parent_fb_id" => Map.get(spec, "parent_fb_id"),
      "state_ref" => "runtime/state/#{Map.get(spec, "mb_id")}.state.json",
      "runtime_state" => Map.get(state, "status", "ready"),
      "last_verification_digest" => Map.get(state, "last_verification_digest")
    })
  end

  defp blocked_dependency?(root, %Issue{blocked_by: blockers}) do
    Enum.any?(blockers, fn mb_id ->
      runtime_state(root, mb_id)
      |> Map.get("status")
      |> Kernel.!=("passed")
    end)
  end

  defp terminal_issue?(%Issue{state: state}) do
    normalize_state(state) in @terminal_states
  end

  defp start_gate_path(root, mb_id), do: Path.join([root, "runtime", "gate_outcomes", mb_id, "attempt_start.json"])
  defp finish_gate_path(root, mb_id), do: latest_attempt_gate_path(root, mb_id, "attempt_finish_gate_outcome.json")

  defp latest_attempt_gate_path(root, mb_id, file_name) do
    root
    |> Path.join("runtime/attempts/#{mb_id}/attempt-*/#{file_name}")
    |> Path.wildcard()
    |> Enum.sort()
    |> List.last()
    |> case do
      nil -> Path.join([root, "runtime", "gate_outcomes", mb_id, file_name])
      path -> path
    end
  end

  defp require_action(%{"symphony_instruction" => %{"action" => action}}, expected) when action == expected, do: :ok
  defp require_action(%{"symphony_instruction" => %{"action" => action}}, expected), do: {:error, {:unexpected_aipd_action, action, expected}}
  defp require_action(_, expected), do: {:error, {:missing_aipd_action, expected}}

  defp require_may_start(%{"symphony_instruction" => %{"may_start_codex" => true}}), do: :ok
  defp require_may_start(_), do: {:error, :aipd_gate_denied_codex_start}

  defp require_finish_action(%{"symphony_instruction" => %{"action" => action}}) when action in @finish_actions, do: :ok
  defp require_finish_action(%{"symphony_instruction" => %{"action" => action}}), do: {:error, {:unknown_finish_action, action}}
  defp require_finish_action(_), do: {:error, :missing_finish_action}

  defp normalize_state(state) when is_binary(state), do: state |> String.trim() |> String.downcase()
  defp normalize_state(_), do: ""

  defp safe_name(value), do: value |> to_string() |> String.replace(~r/[^A-Za-z0-9_.-]/, "_")

  defp generate_start_gate(root, mb_id) do
    run_bridge(["attempt-start", "--project-root", root, "--mb-id", mb_id, "--codex-command", Config.settings!().codex.command])
  end

  defp ensure_start_gate(root, mb_id) do
    if File.exists?(start_gate_path(root, mb_id)), do: :ok, else: generate_start_gate(root, mb_id)
  end

  defp generate_finish_gate(root, workspace_root, mb_id, summary) do
    with {:ok, attempt_id} <- latest_attempt_id(root, mb_id) do
      args = [
        "attempt-finish",
        "--project-root",
        root,
        "--workspace-root",
        workspace_root,
        "--mb-id",
        mb_id,
        "--attempt-id",
        attempt_id
      ]

      args =
        case summary do
          text when is_binary(text) and text != "" -> args ++ ["--summary", text]
          _ -> args
        end

      run_bridge(args)
    end
  end

  defp ensure_finish_gate(root, workspace_root, mb_id, summary) do
    if File.exists?(finish_gate_path(root, mb_id)),
      do: :ok,
      else: generate_finish_gate(root, workspace_root, mb_id, summary)
  end

  defp latest_attempt_id(root, mb_id) do
    root
    |> Path.join("runtime/attempts/#{mb_id}/attempt-*")
    |> Path.wildcard()
    |> Enum.sort()
    |> List.last()
    |> case do
      nil -> {:error, :missing_attempt_id}
      path -> {:ok, Path.basename(path)}
    end
  end

  defp run_bridge(args) do
    bridge = bridge_script_path()

    case System.find_executable("python3") do
      nil ->
        {:error, :python3_not_found}

      python3 ->
        case System.cmd(python3, [bridge | args], stderr_to_stdout: true) do
          {_output, 0} -> :ok
          {output, status} -> {:error, {:aipd_bridge_failed, status, output}}
        end
    end
  end

  defp bridge_script_path do
    Path.expand("../../../../../../scripts/aipd_gate.py", __DIR__)
  end

  def active_states, do: @active_states
  def terminal_states, do: @terminal_states
end
