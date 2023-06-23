"""Simple distance solver using PnP."""
import numpy as np
import cv2
import Utils
from scipy.spatial.transform import Rotation as R

class pnp_estimator:
    """Distance estimator using PnP."""

    def __init__(self, cfg):
        """Initialize the PnP solver.

        Args:
            cfg (object): python config node object
        """
        self.cfg = cfg
        self.K = Utils.get_intrinsic_matrix(self.cfg)

        # 3D armor board coordinates centered at armor board center
        # The unit is in mm (millimeter)
        self.small_armor_3d_pts = np.array([
            [-65, -125 / 4, 0],  # left top
            [-65, 125 / 4, 0],
            [65, -125 / 4, 0],
            [65, 125 / 4, 0]
        ]).reshape((4, 3, 1)) / 1000.0

    def estimate_position(self, armor):
        """Estimate the distance to the armor.

        Args:
            armor (armor): selected armor object

        Returns:
            (armor_xyz, armor_yaw): armor position in camera coordinate and yaw angle
                                    None if PnP fails
        """
        obj_2d_pts = np.array([
            armor.left_light.top.astype(int),
            armor.left_light.btm.astype(int),
            armor.right_light.top.astype(int),
            armor.right_light.btm.astype(int),
        ]).reshape((4, 2, 1))

        # FIXME: distinguish small and large armors
        retval, rvec, tvec = cv2.solvePnP(self.small_armor_3d_pts.astype(float),
                                            obj_2d_pts.astype(float),
                                            self.K,
                                            distCoeffs=None,
                                            flags=cv2.SOLVEPNP_IPPE)
        
        if not retval:
            return None, None

        rot_mat, _ = cv2.Rodrigues(rvec)

        r = R.from_matrix(rot_mat)
        # enemy armor angle w.r.t. enemy robot center
        _, _, armor_yaw = r.as_euler('xyz', degrees=False)
        assert not np.isnan(armor_yaw)

        # Change translation vector from camera coordinate to robot coordinate
        armor_xyz = np.array([tvec[2], tvec[0], tvec[1]])

        return armor_xyz, armor_yaw
