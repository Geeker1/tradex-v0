import zmq
from threading import Thread
import time
import pandas as pd
import os

now = pd.Timestamp.utcnow()
prev = now - pd.Timedelta(hours=6)

hist = {
  "ticks_history": "R_50",
  "end": f"{int(now.timestamp())}",
  "start": int(prev.timestamp()),
  "style": "candles",
  "adjust_start_time": 1,
}


def start(x):
    ctx = zmq.Context()
    sock = ctx.socket(zmq.REQ)
    sock.setsockopt_string(zmq.IDENTITY, f"sock{x}")
    port = os.getenv("InterRouterNo")
    sock.connect(f"tcp://localhost:{port}")
    while True:
        try:
            sock.send_json(hist)
            msg = sock.recv_json()
            print(msg)
            break
        except KeyboardInterrupt:
            print("Interrupted now....")
            sock.close()
            ctx.term()


if __name__ == '__main__':
    thread1 = Thread(target=start, args=(1,))
    thread1.start()
