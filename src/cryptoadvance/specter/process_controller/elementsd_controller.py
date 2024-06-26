from .node_controller import NodePlainController
import tempfile
import logging

logger = logging.getLogger(__name__)


class ElementsPlainController(NodePlainController):
    """A Controller specifically for the Bitcoind-process"""

    def __init__(
        self,
        elementsd_path="elementsd",
        rpcport=18555,
        network="regtest",
        rpcuser="liquid",
        rpcpassword="secret",
    ):
        # Just call super and add the node_impl
        super().__init__(
            "elements",
            node_path=elementsd_path,
            rpcport=rpcport,
            network=network,
            rpcuser=rpcuser,
            rpcpassword=rpcpassword,
        )

    def start_elementsd(
        self,
        cleanup_at_exit=False,
        cleanup_hard=False,
        datadir=None,
        log_stdout=False,
        extra_args=[],
        timeout=60,
    ):
        """starts elementsd with a specific rpcport=18543 by default.
        That's not the standard in order to make pytest running while
        developing locally against a different regtest-instance
        """
        # convenience method
        return self.start_node(
            cleanup_at_exit,
            cleanup_hard,
            datadir,
            log_stdout,
            extra_args,
            timeout,
        )

    def stop_elementsd(self):
        self.stop_node()

    @classmethod
    def construct_node_cmd(
        cls,
        rpcconn,
        run_docker=True,
        datadir=None,
        log_stdout=False,
        node_path="elementsd",
        network="regtest",  # Doesn't make sense here. For now, only "elreg" is supported
        extra_args=[],
    ):
        """returns a command to run your elementsd"""
        btcd_cmd = '"{}" '.format(node_path)
        btcd_cmd += " -chain=elreg "
        btcd_cmd += " -fallbackfee=0.0000001 "
        btcd_cmd += " -validatepegin=0 "
        btcd_cmd += " -txindex=1 "
        btcd_cmd += " -initialfreecoins=2100000000000000 "
        btcd_cmd += " -port={} -rpcport={}".format(rpcconn.rpcport + 1, rpcconn.rpcport)
        btcd_cmd += " -rpcuser={} -rpcpassword={} ".format(
            rpcconn.rpcuser, rpcconn.rpcpassword
        )
        if not run_docker:
            if not log_stdout:
                btcd_cmd += " -noprinttoconsole"
            if datadir is None:
                datadir = tempfile.mkdtemp(prefix="bitcoind_datadir")
            btcd_cmd += ' -datadir="{}" '.format(datadir)
        print(f"extra_args={extra_args})")
        if extra_args:
            btcd_cmd += " {}".format(" ".join(extra_args))
        logger.debug("constructed elementsd-command: %s", btcd_cmd)
        return btcd_cmd

    def version(self):
        """Returns the version of elementsd, e.g. "v0.18.1" """
        version = self.get_rpc().getnetworkinfo()["subversion"]
        version = version.replace("/", "").replace("Elements Core:", "v")
        return version
