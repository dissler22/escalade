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


def test_visual_refresh_contract_lists_reviewed_pages_and_markers():
    contract = Path("specs/003-club-visual-refresh/contracts/openapi.yaml").read_text()
    for required_path in [
        "/login/",
        "/sessions/",
        "/sessions/{occurrenceId}/",
        "/bookings/mine/",
        "/admin/sessions/",
        "/admin/accounts/",
        "/admin/audit/sessions/{occurrenceId}/",
        "/static/css/app.css",
    ]:
        assert required_path in contract

    for required_marker in [
        "x-visual-review",
        "usmv-branding",
        "mobile-readable-layout",
        "admin-dense-layout-readable",
        "responsive-table",
    ]:
        assert required_marker in contract


def test_responsable_management_contract_lists_slot_and_admin_paths():
    contract = Path("specs/004-session-opener-management/contracts/openapi.yaml").read_text()
    for required_path in [
        "/sessions",
        "/sessions/{sessionId}",
        "/session-slots/{slotId}/reservations",
        "/session-slots/{slotId}/responsibility",
        "/admin/accounts/{userId}/responsable-accreditation",
        "/admin/session-slots/{slotId}/responsibility",
    ]:
        assert required_path in contract
