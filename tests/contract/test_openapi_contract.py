from pathlib import Path


def test_openapi_contract_lists_member_and_admin_paths():
    contract = Path("specs/001-free-session-booking/contracts/openapi.yaml").read_text()
    assert "/auth/login" in contract
    assert "/sessions/{sessionId}/reservations" in contract
    assert "/admin/sessions/{sessionId}/status" in contract


def test_deployment_contract_lists_public_smoke_paths():
    contract = Path("specs/002-gcp-vm-deploy/contracts/openapi.yaml").read_text()
    for required_path in ["/", "/login/", "/sessions/", "/bookings/mine/", "/static/css/app.css"]:
        assert required_path in contract
    assert "email" in contract
