defmodule SymphonyElixir.Aipd.GateOutcome do
  @moduledoc """
  Validates AIPD gate outcomes before Symphony acts on them.
  """

  @issue_types [
    "spec_gap",
    "implementation_bug",
    "quality_evidence_gap",
    "state_drift",
    "environment_issue",
    "review_context_gap"
  ]

  @routes ["spec_architect", "builder", "recovery_coordinator", "current_scene_lead"]

  @actions [
    "dispatch_codex",
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

  @spec load(Path.t()) :: {:ok, map()} | {:error, term()}
  def load(path) when is_binary(path) do
    with {:ok, body} <- File.read(path),
         {:ok, decoded} <- Jason.decode(body),
         :ok <- validate(decoded) do
      {:ok, decoded}
    else
      {:error, %Jason.DecodeError{} = error} -> {:error, {:malformed_gate_outcome, path, error}}
      {:error, reason} -> {:error, reason}
    end
  end

  @spec validate(map()) :: :ok | {:error, term()}
  def validate(%{} = outcome) do
    with :ok <- require_value(outcome, "schema_version", "1.0"),
         :ok <- require_in(outcome, "gate", ["attempt_start", "attempt_finish"]),
         :ok <- require_binary(outcome, "mb_id"),
         :ok <- validate_attempt_id(outcome),
         :ok <- validate_aipd_decision(Map.get(outcome, "aipd_decision")),
         :ok <- validate_symphony_instruction(Map.get(outcome, "symphony_instruction")),
         :ok <- require_binary(outcome, "reason"),
         :ok <- validate_non_empty_string_list(outcome, "evidence_refs"),
         :ok <- require_binary(outcome, "state_ref"),
         :ok <- validate_start_semantics(outcome) do
      :ok
    end
  end

  def validate(_), do: {:error, :gate_outcome_not_object}

  @spec allowed_action?(String.t()) :: boolean()
  def allowed_action?(action), do: action in @actions

  defp validate_aipd_decision(%{} = decision) do
    with :ok <- require_binary(decision, "status"),
         :ok <- optional_in(decision, "issue_type", @issue_types),
         :ok <- optional_in(decision, "route_to", @routes),
         :ok <- require_binary(decision, "next_action") do
      :ok
    end
  end

  defp validate_aipd_decision(_), do: {:error, :invalid_aipd_decision}

  defp validate_symphony_instruction(%{} = instruction) do
    with :ok <- require_in(instruction, "action", @actions),
         :ok <- require_boolean(instruction, "may_start_codex"),
         :ok <- require_boolean(instruction, "retryable"),
         :ok <- validate_retry_after(instruction),
         :ok <- validate_codex_start(instruction) do
      :ok
    end
  end

  defp validate_symphony_instruction(_), do: {:error, :invalid_symphony_instruction}

  defp validate_start_semantics(%{"gate" => "attempt_start", "symphony_instruction" => %{"action" => "dispatch_codex"}} = outcome) do
    with :ok <- require_binary(outcome, "attempt_id"),
         :ok <- require_value(outcome["aipd_decision"], "status", "authorized"),
         :ok <- require_value(outcome["aipd_decision"], "issue_type", nil),
         :ok <- require_value(outcome["aipd_decision"], "route_to", nil) do
      :ok
    end
  end

  defp validate_start_semantics(%{"gate" => "attempt_start"} = outcome) do
    require_value(outcome, "attempt_id", nil)
  end

  defp validate_start_semantics(_), do: :ok

  defp validate_attempt_id(%{"attempt_id" => nil}), do: :ok
  defp validate_attempt_id(%{"attempt_id" => value}) when is_binary(value), do: :ok
  defp validate_attempt_id(_), do: {:error, {:missing_or_invalid, "attempt_id"}}

  defp validate_retry_after(%{"retry_after_ms" => nil}), do: :ok
  defp validate_retry_after(%{"retry_after_ms" => value}) when is_integer(value) and value >= 0, do: :ok
  defp validate_retry_after(_), do: {:error, {:missing_or_invalid, "retry_after_ms"}}

  defp validate_codex_start(%{"may_start_codex" => true, "action" => "dispatch_codex"}), do: :ok
  defp validate_codex_start(%{"may_start_codex" => true, "action" => action}), do: {:error, {:unsafe_codex_start, action}}
  defp validate_codex_start(_), do: :ok

  defp require_value(map, key, expected) do
    case Map.fetch(map, key) do
      {:ok, ^expected} -> :ok
      {:ok, value} -> {:error, {:unexpected_value, key, value}}
      :error -> {:error, {:missing_key, key}}
    end
  end

  defp require_binary(map, key) do
    case Map.fetch(map, key) do
      {:ok, value} when is_binary(value) and value != "" -> :ok
      {:ok, value} -> {:error, {:invalid_string, key, value}}
      :error -> {:error, {:missing_key, key}}
    end
  end

  defp require_boolean(map, key) do
    case Map.fetch(map, key) do
      {:ok, value} when is_boolean(value) -> :ok
      {:ok, value} -> {:error, {:invalid_boolean, key, value}}
      :error -> {:error, {:missing_key, key}}
    end
  end

  defp require_in(map, key, allowed) do
    case Map.fetch(map, key) do
      {:ok, value} ->
        if value in allowed, do: :ok, else: {:error, {:invalid_enum, key, value}}

      :error ->
        {:error, {:missing_key, key}}
    end
  end

  defp optional_in(map, key, allowed) do
    case Map.fetch(map, key) do
      {:ok, nil} -> :ok
      {:ok, value} -> if value in allowed, do: :ok, else: {:error, {:invalid_enum, key, value}}
      :error -> {:error, {:missing_key, key}}
    end
  end

  defp validate_non_empty_string_list(map, key) do
    case Map.fetch(map, key) do
      {:ok, values} when is_list(values) and values != [] ->
        if Enum.all?(values, &(is_binary(&1) and &1 != "")), do: :ok, else: {:error, {:invalid_string_list, key}}

      {:ok, value} ->
        {:error, {:invalid_string_list, key, value}}

      :error ->
        {:error, {:missing_key, key}}
    end
  end
end
