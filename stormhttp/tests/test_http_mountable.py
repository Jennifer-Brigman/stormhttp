import asyncio
import unittest
try:
    import uvloop
    asyncio.set_event_loop(uvloop.new_event_loop())
except ImportError:
    pass


class TestMountable(unittest.TestCase):
    def test_simple_mount(self):
        from stormhttp._router import Router, _PREFIX_TREE_MOUNT
        from stormhttp._mountable import AbstractMountable

        router = Router()
        mount = AbstractMountable()
        router.add_mount("/a", mount)
        self.assertEqual(router._prefix_tree, {"a": {_PREFIX_TREE_MOUNT: mount}})

    def test_remount_error(self):
        from stormhttp._router import Router
        from stormhttp._mountable import AbstractMountable

        router = Router()
        mount = AbstractMountable()
        router.add_mount("/a", mount)
        with self.assertRaises(ValueError):
            router.add_mount("/a", mount)

    def test_remount_sub_mount_error(self):
        from stormhttp._router import Router
        from stormhttp._mountable import AbstractMountable

        router = Router()
        mount = AbstractMountable()
        router.add_mount("/a", mount)
        with self.assertRaises(ValueError):
            router.add_mount("/a/b", mount)

    def test_remount_sub_mount_2_error(self):
        from stormhttp._router import Router
        from stormhttp._mountable import AbstractMountable

        router = Router()
        mount = AbstractMountable()
        router.add_mount("/a/b", mount)
        with self.assertRaises(ValueError):
            router.add_mount("/a", mount)

    def test_remount_sub_mount_3_error(self):
        from stormhttp._router import Router
        from stormhttp._mountable import AbstractMountable
        from stormhttp._endpoints import ConstantEndPoint

        router = Router()
        mount = AbstractMountable()
        router.add_endpoint("/a/b", ["GET"], ConstantEndPoint(""))
        with self.assertRaises(ValueError):
            router.add_mount("/a", mount)