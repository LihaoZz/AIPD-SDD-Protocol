defmodule SymphonyElixir.AipdAdapterTest do
  use SymphonyElixir.TestSupport

  alias SymphonyElixir.Aipd.{Adapter, GateOutcome}

  test "config accepts aipd_mb tracker only with an AIPD root" do
    write_workflow_file!(Workflow.workflow_file_path(),
      tracker_kind: "aipd_mb",
      tracker_aipd_root: nil,
      tracker_api_token: nil,
      tracker_project_slug: nil
    )

    assert {:error, :missing_aipd_root} = Config.validate!()

    root = tmp_root("aipd-config")

    try do
      File.mkdir_p!(root)

      write_workflow_file!(Workflow.workflow_file_path(),
        tracker_kind: "aipd_mb",
        tracker_aipd_root: root,
        tracker_api_token: nil,
        tracker_project_slug: nil
      )

      assert :ok = Config.validate!()
      assert Config.settings!().tracker.aipd_root == root
    after
      File.rm_rf(root)
    end
  end

  test "AIPD adapter maps machine specs and runtime state to issues" do
    root = tmp_root("aipd-adapter")

    try do
      create_aipd_project!(root)
      write_machine_spec!(root, "fb1-mb1", "Build first MB")
      write_state!(root, "fb1-mb1", %{"status" => "passed", "review_required" => true, "last_verification_digest" => "ok"})

      configure_aipd!(root)

      assert {:ok, [issue]} = Tracker.fetch_candidate_issues()
      assert issue.id == "fb1-mb1"
      assert issue.identifier == "fb1-mb1"
      assert issue.title == "Build first MB"
      assert issue.state == "review"
      assert issue.blocked_by == []
      assert issue.description =~ "last_verification_digest"
    after
      File.rm_rf(root)
    end
  end

  test "AIPD adapter filters unresolved blocked_by_mbs dependencies" do
    root = tmp_root("aipd-adapter-blocked")

    try do
      create_aipd_project!(root)
      write_machine_spec!(root, "fb1-mb1", "Build dependent MB", %{"blocked_by_mbs" => ["fb1-mb0"]})
      configure_aipd!(root)

      assert {:ok, []} = Tracker.fetch_candidate_issues()

      write_machine_spec!(root, "fb1-mb0", "Build blocker")
      write_state!(root, "fb1-mb0", %{"status" => "passed", "review_required" => false})

      assert {:ok, [issue]} = Tracker.fetch_candidate_issues()
      assert issue.id == "fb1-mb1"
      assert issue.blocked_by == ["fb1-mb0"]
    after
      File.rm_rf(root)
    end
  end

  test "gate outcome validator fails closed for unknown action and unsafe Codex start" do
    valid = start_gate("fb1-mb1", "dispatch_codex", true)

    assert :ok = GateOutcome.validate(valid)

    assert {:error, {:invalid_enum, "action", "invent_action"}} =
             GateOutcome.validate(put_in(valid, ["symphony_instruction", "action"], "invent_action"))

    unsafe =
      valid
      |> put_in(["symphony_instruction", "action"], "release_and_pause")
      |> put_in(["symphony_instruction", "may_start_codex"], true)

    assert {:error, {:unsafe_codex_start, "release_and_pause"}} = GateOutcome.validate(unsafe)
  end

  test "adapter claim and finish accept only validated gate outcomes" do
    root = tmp_root("aipd-gates")

    try do
      create_aipd_project!(root)
      write_machine_spec!(root, "fb1-mb1", "Build gated MB")
      configure_aipd!(root)
      issue = %Issue{id: "fb1-mb1", identifier: "fb1-mb1"}

      assert :ok = Adapter.claim_issue(issue)

      write_start_gate!(root, "fb1-mb1", start_gate("fb1-mb1", "release_and_pause", false))
      assert {:error, {:unexpected_aipd_action, "release_and_pause", "dispatch_codex"}} = Adapter.claim_issue(issue)

      write_start_gate!(root, "fb1-mb1", start_gate("fb1-mb1", "dispatch_codex", true))
      assert :ok = Adapter.claim_issue(issue)

      write_finish_gate!(root, "fb1-mb1", finish_gate("fb1-mb1", "release_to_review"))
      assert :ok = Adapter.finish_issue(issue, root, nil)
    after
      File.rm_rf(root)
    end
  end

  test "agent runner checks AIPD start gate before creating workspace" do
    root = tmp_root("aipd-runner")
    workspace_root = tmp_root("aipd-runner-workspace")

    try do
      create_aipd_project!(root)
      write_machine_spec!(root, "fb1-mb1", "Build guarded MB")
      File.rm!(Path.join([root, "function_blocks", "fb1.md"]))

      write_workflow_file!(Workflow.workflow_file_path(),
        tracker_kind: "aipd_mb",
        tracker_aipd_root: root,
        tracker_api_token: nil,
        tracker_project_slug: nil,
        workspace_root: workspace_root
      )

      issue = %Issue{id: "fb1-mb1", identifier: "fb1-mb1"}

      assert_raise RuntimeError, ~r/aipd_bridge_failed/, fn ->
        AgentRunner.run(issue)
      end

      refute File.exists?(Path.join(workspace_root, "fb1-mb1"))
    after
      File.rm_rf(root)
      File.rm_rf(workspace_root)
    end
  end

  defp configure_aipd!(root) do
    write_workflow_file!(Workflow.workflow_file_path(),
      tracker_kind: "aipd_mb",
      tracker_aipd_root: root,
      tracker_api_token: nil,
      tracker_project_slug: nil
    )
  end

  defp create_aipd_project!(root) do
    File.mkdir_p!(Path.join(root, "missions"))
    File.mkdir_p!(Path.join(root, "function_blocks"))
    File.mkdir_p!(Path.join(root, "runtime/state"))
    File.write!(Path.join(root, "function_blocks/fb1.md"), "# Function Block\n")
  end

  defp write_machine_spec!(root, mb_id, goal, concurrency \\ %{}) do
    [parent_fb_id] = Regex.run(~r/^(fb\d+)-mb\d+$/, mb_id, capture: :all_but_first)

    spec = %{
      "schema_version" => "1.0",
      "mb_id" => mb_id,
      "parent_fb_id" => parent_fb_id,
      "goal" => goal,
      "context_files" => ["src/app.py"],
      "input_artifacts" => [],
      "allowed_touch" => ["src/app.py"],
      "forbidden_touch" => [],
      "acceptance" => [
        %{
          "check_id" => "scope_ok",
          "type" => "no_out_of_scope_changes"
        }
      ],
      "retry_policy" => %{
        "max_retries" => 3,
        "on_retry_limit" => "route_to_recovery"
      },
      "prompt_feedback" => %{
        "include_last_verification_digest" => true,
        "include_last_failure_reason" => true,
        "include_retry_count" => true
      },
      "issue_owner_map" => %{
        "spec_gap" => "spec_architect",
        "implementation_bug" => "builder",
        "quality_evidence_gap" => "builder",
        "state_drift" => "recovery_coordinator",
        "environment_issue" => "recovery_coordinator",
        "review_context_gap" => "current_scene_lead"
      },
      "concurrency" => concurrency
    }

    File.write!(Path.join([root, "missions", "#{mb_id}.machine.json"]), Jason.encode!(spec))
    File.write!(Path.join([root, "missions", "#{mb_id}.md"]), "# Mission Block\n")
  end

  defp write_state!(root, mb_id, fields) do
    state =
      Map.merge(
        %{
          "schema_version" => "1.0",
          "mb_id" => mb_id,
          "status" => "ready",
          "review_required" => false,
          "last_verification_digest" => nil
        },
        fields
      )

    File.write!(Path.join([root, "runtime", "state", "#{mb_id}.state.json"]), Jason.encode!(state))
  end

  defp write_start_gate!(root, mb_id, outcome) do
    dir = Path.join([root, "runtime", "gate_outcomes", mb_id])
    File.mkdir_p!(dir)
    File.write!(Path.join(dir, "attempt_start.json"), Jason.encode!(outcome))
  end

  defp write_finish_gate!(root, mb_id, outcome) do
    dir = Path.join([root, "runtime", "attempts", mb_id, "attempt-001"])
    File.mkdir_p!(dir)
    File.write!(Path.join(dir, "attempt_finish_gate_outcome.json"), Jason.encode!(outcome))
  end

  defp start_gate(mb_id, action, may_start) do
    %{
      "schema_version" => "1.0",
      "gate" => "attempt_start",
      "mb_id" => mb_id,
      "attempt_id" => if(action == "dispatch_codex", do: "attempt-001", else: nil),
      "aipd_decision" => %{
        "status" => if(action == "dispatch_codex", do: "authorized", else: "blocked"),
        "issue_type" => if(action == "dispatch_codex", do: nil, else: "spec_gap"),
        "route_to" => if(action == "dispatch_codex", do: nil, else: "spec_architect"),
        "next_action" => "start_codex"
      },
      "symphony_instruction" => %{
        "action" => action,
        "may_start_codex" => may_start,
        "retryable" => false,
        "retry_after_ms" => nil
      },
      "reason" => "test",
      "evidence_refs" => ["runtime/preflight/mb_preflight_#{mb_id}.json"],
      "state_ref" => "runtime/state/#{mb_id}.state.json"
    }
  end

  defp finish_gate(mb_id, action) do
    %{
      "schema_version" => "1.0",
      "gate" => "attempt_finish",
      "mb_id" => mb_id,
      "attempt_id" => "attempt-001",
      "aipd_decision" => %{
        "status" => "passed",
        "issue_type" => nil,
        "route_to" => nil,
        "next_action" => "handoff_to_review"
      },
      "symphony_instruction" => %{
        "action" => action,
        "may_start_codex" => false,
        "retryable" => false,
        "retry_after_ms" => nil
      },
      "reason" => "test",
      "evidence_refs" => ["runtime/attempts/#{mb_id}/attempt-001/verification_report.json"],
      "state_ref" => "runtime/state/#{mb_id}.state.json"
    }
  end

  defp tmp_root(prefix) do
    Path.join(System.tmp_dir!(), "#{prefix}-#{System.unique_integer([:positive])}")
  end
end
