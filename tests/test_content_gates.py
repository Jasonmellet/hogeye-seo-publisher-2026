"""Gates for the HogEye writing loop (WRITING_LOOP.md phases 0, 5, and 6).

    ./.venv/bin/python -m pytest -q tests
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "seo"))

from hogeye_content_quality import validate_item  # noqa: E402
from validate_he_briefs import validate_brief  # noqa: E402

REJECTED = REPO_ROOT / "workspace" / "content_pipeline" / "monthly" / "2026-10" / "_rejected_2026-10-19" / "content_posts"


def _post(body: str, **extra) -> dict:
    post = {
        "externalId": "oct26_09",
        "period": "2026-10",
        "title": "How to Count Hogs Before You Close the Trap",
        "meta_title": "Count Hogs on Trail Camera Before You Close",
        "meta_description": "Count every hog for a few nights, then close.",
        "focus_keyword": "count hogs on trail camera",
        "content": body,
        "targetWordCount": 750,
        "minWords": 450,
    }
    post.update(extra)
    return post


def _body(sentences: int) -> str:
    """Filler of 17 distinct words per sentence, so only the sentence under test can repeat."""
    return "\n".join("<p>" + " ".join(f"w{i}x{j}" for j in range(17)) + ".</p>" for i in range(sentences))


def _labels(report: dict) -> list[str]:
    return [f["label"] for f in report["findings"]]


def _brief(**extra) -> dict:
    brief = {
        "brief_id": "oct26_05",
        "external_id": "oct26_05",
        "period": "2026-10",
        "type": "new",
        "title": "How to Count Hogs on Camera",
        "slug": "count-hogs-on-trail-camera",
        "target_keyword": "count hogs on trail camera",
        "reader_sentence": "Count every hog for three nights and close only when that number is inside.",
        "sentence_approved": {"by": "Jason", "on": "2026-10-21"},
        "evidence": [{"source": "gsc", "signal": "120 impressions/90d"}],
        "word_count": 750,
        "min_words": 450,
        "key_points": ["The HogEye Mini Camera streams live video to the HogEye app."],
        "internal_links": [],
        "categories": ["Feral Hog Monitoring"],
    }
    brief.update(extra)
    return brief


# --- length is a range, not a band ------------------------------------------------

def test_length_inside_range_passes():
    report = validate_item(_post(_body(35)))
    assert report["ok"], report


def test_short_piece_is_a_warning_not_a_fail():
    report = validate_item(_post(_body(10)))
    assert report["ok"]
    assert any("floor" in w for w in report["warnings"])


def test_over_ceiling_fails():
    report = validate_item(_post(_body(50)))
    assert not report["ok"]
    assert any("ceiling" in e for e in report["errors"])


def test_old_800_band_is_gone():
    # 700 words against an 800 target used to fail the ±5% band.
    report = validate_item(_post(_body(41), targetWordCount=800, minWords=None))
    assert report["ok"], report


# --- brief rules written as prose ------------------------------------------------

@pytest.mark.parametrize(
    "sentence",
    [
        "The camera does not close the gate by itself.",
        "It does not close the gate by itself.",
        "The hog cam does not close a gate, drop a net, or trip an actuator on its own.",
        "The camera does not decide that the sounder is complete.",
        "It is not a general property camera.",
        "HogEye is not a security camera.",
        "This guide walks through the count.",
    ],
)
def test_rule_as_prose_fails(sentence):
    report = validate_item(_post(_body(40) + f"<p>{sentence}</p>"))
    assert not report["ok"], sentence


def test_trail_camera_contrast_passes():
    report = validate_item(_post(_body(40) + "<p>A trail camera can't close the gate, so you drive out to do it.</p>"))
    assert report["ok"], report


def test_reader_sending_the_command_passes():
    report = validate_item(_post(_body(40) + "<p>When all nine are inside, tap close in the app and the gate drops.</p>"))
    assert report["ok"], report


def test_rejected_october_drafts_fail():
    files = sorted(REJECTED.glob("oct26_0*_wp_draft.json"))
    assert len(files) == 5
    for path in files:
        report = validate_item(json.loads(path.read_text(encoding="utf-8")))
        assert not report["ok"], path.name


def test_tldr_is_optional_but_sized_when_present():
    assert validate_item(_post(_body(35)))["ok"]
    short = "<p><strong>TL;DR:</strong> Close when they are all in.</p>\n"
    assert "TL;DR must be 35-60 words" in _labels(validate_item(_post(short + _body(35))))


# --- repeats ---------------------------------------------------------------------

def test_repeated_sentence_fails():
    report = validate_item(_post(_body(40) + "<p>You send the closure command from the app.</p>" * 2))
    assert "repeated sentence" in _labels(report)


def test_phrase_repeated_three_times_fails():
    phrase = "close when the full sounder is inside the trap"
    body = _body(40) + "".join(f"<p>Night {n}: {phrase} and not before.</p>" for n in ("one", "two", "three"))
    assert any("repeated" in label for label in _labels(validate_item(_post(body))))


# --- brand policy ----------------------------------------------------------------

def test_trail_camera_keyword_is_allowed():
    report = validate_item(_post(_body(40) + "<p>A trail camera sends a photo; the HogEye app shows the trap live.</p>"))
    assert report["ok"], report


@pytest.mark.parametrize(
    "sentence",
    [
        "HogEye is a trail camera for hogs.",
        "Most ranchers start with one trap.",
        "Mount the HogEye Steel on the panel.",
        "The Steel Camera covers the gate.",
        "The Mini AI camera spots the boar.",
        "Treat screwworm wounds with spray.",
        "Count the hogs — then close.",
        "Use the camera for property security.",
    ],
)
def test_brand_policy_fails(sentence):
    assert not validate_item(_post(_body(40) + f"<p>{sentence}</p>"))["ok"], sentence


def test_prices_must_come_from_product_facts():
    assert validate_item(_post(_body(40) + "<p>The HogEye Mini Camera is $1,299.</p>"))["ok"]
    report = validate_item(_post(_body(40) + "<p>The HogEye Mini Camera is $999.</p>"))
    assert "price not in PRODUCT_FACTS.md" in _labels(report)


# --- brief contract --------------------------------------------------------------

def test_complete_brief_passes():
    assert validate_brief(_brief()) == []


@pytest.mark.parametrize("field", ["reader_sentence", "sentence_approved", "evidence"])
def test_october_brief_needs_sentence_and_evidence(field):
    brief = _brief()
    del brief[field]
    assert any(e.startswith(field) for e in validate_brief(brief))


def test_september_brief_does_not_need_sentence():
    brief = _brief(period="2026-09")
    for field in ("reader_sentence", "sentence_approved", "evidence"):
        del brief[field]
    assert validate_brief(brief) == []


def test_slot_filler_fails():
    errors = validate_brief(_brief(why_this_month="Fills the paid count for October."))
    assert any("paid slot" in e for e in errors)


def test_rule_in_key_points_fails():
    errors = validate_brief(_brief(key_points=["Do not claim the camera closes the gate by itself."]))
    assert any("rule for the writer" in e for e in errors)


def test_pending_facts_hold_the_brief():
    errors = validate_brief(_brief(facts_pending=["Spartan GoLive price from Spartan's site"]))
    assert any(e.startswith("facts_pending") for e in errors)


def test_refresh_needs_existing_url():
    assert any(e.startswith("existing_url") for e in validate_brief(_brief(type="update")))


def test_floor_must_be_below_ceiling():
    assert any(e.startswith("min_words") for e in validate_brief(_brief(min_words=800)))


# --- canonical loop ----------------------------------------------------------------

def test_writing_loop_is_a_pointer_not_a_copy():
    # One copy of the doctrine lives in the parent folder; the repo only points to it.
    stub = (REPO_ROOT / "docs" / "WRITING_LOOP.md").read_text()
    assert "../WRITING_LOOP.md" in stub
    assert len(stub.splitlines()) < 15
