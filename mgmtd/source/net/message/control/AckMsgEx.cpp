#include <program/Program.h>
#include "AckMsgEx.h"

bool AckMsgEx::processIncoming(ResponseContext& ctx)
{
   LogContext log("Ack incoming");

   #ifdef CONGFS_DEBUG
      LOG_DEBUG_CONTEXT(log, 5, std::string("Value: ") + getValue() );
   #endif // CONGFS_DEBUG
   
   AcknowledgmentStore* ackStore = Program::getApp()->getAckStore();
   ackStore->receivedAck(getValue() );
   
   // note: this message does not require a response
   
   return true;
}


