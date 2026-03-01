import { useParams, useSearchParams } from "react-router-dom";
import { useEffect } from "react";
import { toast } from "react-toastify";
import {
  markPlatformInvoicePaid,
  recordPlatformTellerPayment,
  recordPlatformBankTransfer,
  initPlatformPaystackPayment,
  initPlatformOpayPayment,
} from "../../services/platformApi"; // ✅ ensure file name matches exactly

const PlatformInvoicePaymentOptions = () => {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const method = searchParams.get("method"); // cash, teller, bank-transfer, paystack, opay

  // Auto-run payment if ?method= is present
  useEffect(() => {
    const runPayment = async () => {
      try {
        switch (method) {
          case "cash":
            await markPlatformInvoicePaid(id);
            toast.success("Platform invoice marked as paid (Cash)");
            break;
          case "teller":
            await recordPlatformTellerPayment(id);
            toast.info("Teller payment recorded. Awaiting confirmation.");
            break;
          case "bank-transfer":
            await recordPlatformBankTransfer(id);
            toast.info("Bank transfer recorded. Awaiting confirmation.");
            break;
          case "paystack":
            const paystackData = await initPlatformPaystackPayment(id);
            if (paystackData.status === "success") {
              window.location.href = paystackData.authorization_url;
            } else {
              toast.error("Paystack error: " + paystackData.message);
            }
            break;
          case "opay":
            const opayData = await initPlatformOpayPayment(id);
            if (opayData.status === "success") {
              window.location.href = opayData.authorization_url;
            } else {
              toast.error("Opay error: " + opayData.message);
            }
            break;
          default:
            // No method provided, do nothing
            break;
        }
      } catch (err) {
        toast.error("Unexpected error: " + err.message);
      }
    };

    if (method) {
      runPayment();
    }
  }, [method, id]);

  // Manual buttons (fallback if no ?method= provided)
  const handleCash = () => markPlatformInvoicePaid(id).then(() => toast.success("Platform invoice marked as paid (Cash)")).catch(() => toast.error("Failed to mark invoice as paid"));
  const handleTeller = () => recordPlatformTellerPayment(id).then(() => toast.info("Teller payment recorded. Awaiting confirmation.")).catch(() => toast.error("Failed to record teller payment"));
  const handleBankTransfer = () => recordPlatformBankTransfer(id).then(() => toast.info("Bank transfer recorded. Awaiting confirmation.")).catch(() => toast.error("Failed to record bank transfer"));
  const handlePaystack = async () => {
    try {
      const data = await initPlatformPaystackPayment(id);
      if (data.status === "success") {
        window.location.href = data.authorization_url;
      } else {
        toast.error("Paystack error: " + data.message);
      }
    } catch (err) {
      toast.error("Unexpected error: " + err.message);
    }
  };
  const handleOpay = async () => {
    try {
      const data = await initPlatformOpayPayment(id);
      if (data.status === "success") {
        window.location.href = data.authorization_url;
      } else {
        toast.error("Opay error: " + data.message);
      }
    } catch (err) {
      toast.error("Unexpected error: " + err.message);
    }
  };

  return (
    <section>
      <h2>Platform Invoice Payment Options</h2>
      <p>Invoice ID: {id}</p>
      <p>Method: {method || "none selected"}</p>

      {/* Manual buttons (if user navigates without ?method=) */}
      <ul>
        <li><button onClick={handleCash}>Cash</button></li>
        <li><button onClick={handleTeller}>Teller</button></li>
        <li><button onClick={handleBankTransfer}>Bank Transfer</button></li>
        <li><button onClick={handlePaystack}>Paystack</button></li>
        <li><button onClick={handleOpay}>Opay</button></li>
      </ul>
    </section>
  );
};

export default PlatformInvoicePaymentOptions;
