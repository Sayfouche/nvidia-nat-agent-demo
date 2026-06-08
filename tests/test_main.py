from training_nvidia_nat.main import load_nvidia_api_key, main


def test_load_nvidia_api_key_from_env_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("NVIDIA_API_KEY=test-key\n")
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)

    assert load_nvidia_api_key(env_file) == "test-key"


def test_main_reports_loaded_key(capsys, monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "test-key")

    main()

    captured = capsys.readouterr()
    assert "API key loaded: Yes" in captured.out
