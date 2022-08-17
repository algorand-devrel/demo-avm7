from typing import Literal

from pyteal import *
from beaker import *


class DemoAVM7(Application):
    """Examples for teal ops that are new for AVM 7"""

    VrfProof = abi.StaticArray[abi.Byte, Literal[80]]
    VrfHash = abi.StaticArray[abi.Byte, Literal[64]]

    @external
    def vrf_verify(
        self,
        msg: abi.DynamicArray[abi.Byte],
        proof: VrfProof,
        pub_key: abi.Address,
        *,
        output: VrfHash,
    ):
        """Verify that some message was used to generate a proof generated by a given public key"""
        return Seq(
            # Use the Algorand VRF
            vrf_result := VrfVerify.algorand(
                # Note: in practice the message is likely to be something like:
                #    sha512_256(concat(itob(round), block.seed(round)))
                # Get the bytes from the message (chop off 2 as they're the uint16 encoded length)
                Suffix(msg.encode(), Int(2)),
                # Get the bytes from the proof
                proof.encode(),
                # Note: in practice this is likely to be some hardcoded public key or one of
                #   a set of "pre-approved" public keys
                # Get the pubkey bytes
                pub_key.encode(),
            ),
            # Check Successful
            Assert(vrf_result.output_slots[1].load() == Int(1)),
            # Write the result to the output
            output.decode(vrf_result.output_slots[0].load()),
        )

    JsonExampleResult = abi.Tuple3[abi.String, abi.Uint64, abi.String]

    @external
    def json_ref(self, json_str: abi.String, *, output: JsonExampleResult):
        return Seq(
            (s := abi.String()).set(
                JsonRef.as_string(json_str.get(), Bytes("string_key"))
            ),
            (i := abi.Uint64()).set(
                JsonRef.as_uint64(json_str.get(), Bytes("uint_key"))
            ),
            (o := abi.String()).set(
                JsonRef.as_object(json_str.get(), Bytes("obj_key"))
            ),
            output.set(s, i, o),
        )

    BlockSeed = abi.StaticArray[abi.Byte, Literal[32]]
    BlockDetails = abi.Tuple2[abi.Uint64, BlockSeed]

    @external
    def block(self, round: abi.Uint64, *, output: BlockDetails):
        """New block operations for getting timestamp or seed of a historical round"""
        return Seq(
            (ts := abi.Uint64()).set(Block.timestamp(round.get())),
            (seed := abi.make(self.BlockSeed)).decode(Block.seed(round.get())),
            output.set(ts, seed),
        )

    @external
    def b64decode(self, b64encoded: abi.String, *, output: abi.String):
        """Base64Decode can be used to decode either a std or url encoded string

        Note:
            IF you have the option to decode prior to submitting the app call
            transaction, you _should_.
            This should _only_ be used in the case that there is no way to decode
            the bytestring prior to submitting the transaction.
        """
        return output.set(Base64Decode.std(b64encoded.get()))

    @external
    def sha3_256(self, to_hash: abi.String, *, output: abi.DynamicArray[abi.Byte]):
        return Seq(
            (tmp := abi.String()).set(Sha3_256(to_hash.get())),
            output.decode(tmp.encode()),
        )

    @external
    def replace(self):
        # replace2
        # replace3
        return Approve()

    @external
    def ed25519verify_bare(self):
        # ed25519verify_bare
        return Approve()

    @external
    def noop(self):
        return Approve()

    @delete(authorize=Authorize.only(Global.creator_address()))
    def delete(self):
        return Approve()
