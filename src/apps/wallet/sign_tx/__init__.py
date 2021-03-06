from trezor import ui, wire
from trezor.messages.MessageType import TxAck
from trezor.messages.RequestType import TXFINISHED
from trezor.messages.TxRequest import TxRequest

from apps.common import paths
from apps.wallet.sign_tx import (
    addresses,
    helpers,
    layout,
    multisig,
    progress,
    scripts,
    segwit_bip143,
    signing,
)


@ui.layout
async def sign_tx(ctx, msg, keychain):
    signer = signing.sign_tx(msg, keychain)

    res = None
    while True:
        try:
            req = signer.send(res)
        except signing.SigningError as e:
            raise wire.Error(*e.args)
        except multisig.MultisigError as e:
            raise wire.Error(*e.args)
        except addresses.AddressError as e:
            raise wire.Error(*e.args)
        except scripts.ScriptsError as e:
            raise wire.Error(*e.args)
        except segwit_bip143.Bip143Error as e:
            raise wire.Error(*e.args)
        if isinstance(req, TxRequest):
            if req.request_type == TXFINISHED:
                break
            res = await ctx.call(req, TxAck)
        elif isinstance(req, helpers.UiConfirmOutput):
            res = await layout.confirm_output(ctx, req.output, req.coin)
            progress.report_init()
        elif isinstance(req, helpers.UiConfirmTotal):
            res = await layout.confirm_total(ctx, req.spending, req.fee, req.coin)
            progress.report_init()
        elif isinstance(req, helpers.UiConfirmFeeOverThreshold):
            res = await layout.confirm_feeoverthreshold(ctx, req.fee, req.coin)
            progress.report_init()
        elif isinstance(req, helpers.UiConfirmForeignAddress):
            res = await paths.show_path_warning(ctx, req.address_n)
        else:
            raise TypeError("Invalid signing instruction")
    return req
