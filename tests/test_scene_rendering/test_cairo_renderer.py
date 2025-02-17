import os
from unittest.mock import Mock, patch

from manim import *

from ..assert_utils import assert_file_exists
from .simple_scenes import *


def test_render(using_temp_config, disabling_caching):
    scene = SquareToCircle()
    renderer = scene.renderer
    renderer.update_frame = Mock(wraps=renderer.update_frame)
    renderer.add_frame = Mock(wraps=renderer.add_frame)
    scene.render()
    assert renderer.add_frame.call_count == config["frame_rate"]
    assert renderer.update_frame.call_count == config["frame_rate"]
    assert_file_exists(config["output_file"])


def test_skipping_status_with_from_to_and_up_to(using_temp_config, disabling_caching):
    """Test if skip_animations is well updated when -n flag is passed"""
    config.from_animation_number = 2
    config.upto_animation_number = 6

    class SceneWithMultipleCalls(Scene):
        def construct(self):
            number = Integer(0)
            self.add(number)
            for i in range(10):
                self.play(Animation(Square()))

                assert ((i >= 2) and (i <= 6)) or self.renderer.skip_animations

    SceneWithMultipleCalls().render()


def test_when_animation_is_cached(using_temp_config):
    scene = SquareToCircle()
    # Render twice to create a cache.
    scene.render()
    pmf = scene.renderer.file_writer.partial_movie_files
    scene = SquareToCircle()
    scene.update_to_time = Mock()
    scene.render()
    assert scene.renderer.file_writer.is_already_cached(
        scene.renderer.animations_hashes[0]
    )
    # Check that the same partial movie files has been used (with the same hash)
    assert pmf == scene.renderer.file_writer.partial_movie_files
    # Check that manim correctly skipped the animation.
    scene.update_to_time.assert_called_once_with(1)
    # Check that the output video has been generated.
    assert_file_exists(config["output_file"])


def test_hash_logic_is_not_called_when_caching_is_disabled(
    using_temp_config, disabling_caching
):
    with patch("manim.renderer.cairo_renderer.get_hash_from_play_call") as mocked:
        scene = SquareToCircle()
        scene.render()
        mocked.assert_not_called()
        assert_file_exists(config["output_file"])


def test_hash_logic_is_called_when_caching_is_enabled(using_temp_config):
    from manim.renderer.cairo_renderer import get_hash_from_play_call

    with patch(
        "manim.renderer.cairo_renderer.get_hash_from_play_call",
        wraps=get_hash_from_play_call,
    ) as mocked:
        scene = SquareToCircle()
        scene.render()
        mocked.assert_called_once()
