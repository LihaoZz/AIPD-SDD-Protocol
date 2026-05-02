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
    "dispatch_agent",
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
         :ok <- require_boolean_alias(instruction, "may_start_agent", "may_start_codex"),
         :ok <- validate_execution_provider(instruction),
         :ok <- require_boolean(instruction, "retryable"),
         :ok <- validate_retry_after(instruction),
         :ok <- validate_agent_start(instruction) do
      :ok
    end
  end

  defp validate_symphony_instruction(_), do: {:error, :invalid_symphony_instruction}

  defp validate_start_semantics(
         %{
           "gate" => "attempt_start",
           "symphony_instruction" => %{"action" => action}
         } = outcome
       )
       when action in ["dispatch_agent", "dispatch_codex"] do
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

  defp validate_execution_provider(%{"action" => action} = instruction)
       when action in ["dispatch_agent", "dispatch_codex"] do
    case Map.get(instruction, "execution_provider") do
      provider when provider in ["codex", "minimax"] -> :ok
      value -> {:error, {:invalid_execution_provider, value}}
    end
  end

  defp validate_execution_provider(%{"execution_provider" => nil}), do: :ok
  defp validate_execution_provider(%{} = instruction) do
    if Map.has_key?(instruction, "execution_provider") do
      {:error, {:invalid_execution_provider, Map.get(instruction, "execution_provider")}}
    else
      :ok
    end
  end

  defp validate_execution_provider(_), do: {:error, {:missing_or_invalid, "execution_provider"}}

  defp validate_agent_start(instruction) do
    may_start = Map.get(instruction, "may_start_agent", Map.get(instruction, "may_start_codex", false))
    action = Map.get(instruction, "action")

    cond do
      may_start == true and action in ["dispatch_agent", "dispatch_codex"] -> :ok
      may_start == true -> {:error, {:unsafe_agent_start, action}}
      true -> :ok
    end
  end

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

  defp require_boolean_alias(map, primary_key, legacy_key) do
    case {Map.fetch(map, primary_key), Map.fetch(map, legacy_key)} do
      {{:ok, value}, _} when is_boolean(value) -> :ok
      {_, {:ok, value}} when is_boolean(value) -> :ok
      {{:ok, value}, _} -> {:error, {:invalid_boolean, primary_key, value}}
      {_, {:ok, value}} -> {:error, {:invalid_boolean, legacy_key, value}}
      _ -> {:error, {:missing_key, primary_key}}
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
