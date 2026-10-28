"""The WordPress client must never change a post that is not a draft."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "packages" / "core_py" / "src"))

from agt_publisher_core.modules.wp_client import LivePostGuardError, WordPressClient  # noqa: E402


class FakeResp:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


class FakeSession:
    def __init__(self, current_status):
        self.current_status = current_status
        self.posts = []

    def get(self, url, params=None, timeout=30):
        return FakeResp(200, '{"status": "%s"}' % self.current_status)

    def post(self, url, params=None, json=None, timeout=30):
        self.posts.append((url, json))
        return FakeResp(200, '{"id": 1}')


@pytest.mark.parametrize("live", ["publish", "future", "private", "pending"])
def test_refuses_to_write_a_non_draft_post(live):
    session = FakeSession(live)
    with pytest.raises(LivePostGuardError):
        WordPressClient(session).post_json("posts/123", {"status": "draft", "content": "x"})
    assert session.posts == []


def test_refuses_to_write_a_live_page():
    session = FakeSession("publish")
    with pytest.raises(LivePostGuardError):
        WordPressClient(session).post_json("pages/9", {"content": "x"})
    assert session.posts == []


def test_refuses_to_publish_new_post():
    session = FakeSession("draft")
    with pytest.raises(LivePostGuardError):
        WordPressClient(session).post_json("posts", {"status": "publish", "title": "t"})
    assert session.posts == []


def test_updates_a_draft_and_creates_drafts():
    session = FakeSession("draft")
    client = WordPressClient(session)
    assert client.post_json("posts/123", {"status": "draft", "content": "x"}).ok
    assert client.post_json("posts", {"status": "draft", "title": "t"}).ok
    assert client.post_json("media/5", {"alt_text": "hog"}).ok
    assert len(session.posts) == 3
