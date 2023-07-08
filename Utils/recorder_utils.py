"""Recorder that saves images into separate videos."""
import os
import shutil
import time
import numpy as np
import cv2


class split_video_recorder:
    """Recorder that saves images into separate videos."""

    def __init__(self, config, TIME_PER_CLIP=20):
        """Initialize the recorder.

        Args:
            config(python object): config python node
            TIME_PER_CLIP(int): time per clip in seconds
        """
        self.CFG = config
        self.TIME_PER_CLIP = TIME_PER_CLIP
        self.base_data_folder = self.CFG.LOGGING_FOLDER
        # Determine folder
        fn_list = [fn for fn in os.listdir(self.base_data_folder) if fn.isdigit()]
        if fn_list:
            max_idx = max([int(fn) for fn in fn_list])
        else:
            max_idx = 0
        new_idx = max_idx + 1
        self.cur_data_folder = os.path.join(
            self.base_data_folder,
            str(new_idx).zfill(8))
        assert not os.path.exists(self.cur_data_folder)
        os.makedirs(self.cur_data_folder)
        self.cur_video_writer = None
        self.cur_video_clip_idx = 0

    def process_one_frame(self, raw_img_bgr):
        """Process one frame.

        Args:
            resized_bgr_frame(numpy array): resized bgr frame
        """
        if self.cur_video_writer is None:
            cur_free_space = shutil.disk_usage(self.base_data_folder).free  # in bytes
            cur_free_space = cur_free_space / 1024 / 1024 / 1024  # in GB
            if cur_free_space < 0.5:  # 500 MB
                print("Not enough space left on disk. Idling...")
                return
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_fn = os.path.join(self.cur_data_folder, "video_{}.mp4".format(self.cur_video_clip_idx))
            # FIXME(roger): save raw videos
            self.cur_video_writer = cv2.VideoWriter(
                video_fn, fourcc, 30, (self.CFG.IMG_WIDTH * 2, self.CFG.IMG_HEIGHT * 2))
            self.writer_start_time = time.time()

        assert self.cur_video_writer is not None
        assert raw_img_bgr is not None
        assert raw_img_bgr.shape == (self.CFG.IMG_HEIGHT * 2, self.CFG.IMG_WIDTH * 2, 3)

        self.cur_video_writer.write(raw_img_bgr)

        if time.time() - self.writer_start_time > self.TIME_PER_CLIP:
            self.cur_video_writer.release()
            self.cur_video_writer = None
            self.cur_video_clip_idx += 1