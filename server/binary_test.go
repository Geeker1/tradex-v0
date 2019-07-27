package main
import(
	"log"
	zmq "github.com/pebbe/zmq4"
	"github.com/gorilla/websocket"
	"net/http"
	"testing"
	"strconv"
	"time"
	"encoding/json"
	"os"
)

func Init() BinaryApi {
	binaryApi := BinaryApi{
		Bs: BinaryServer{
			Dialer: websocket.Dialer{},
			Header: http.Header{},
			Url: "wss://ws.binaryws.com/websockets/v3?app_id="+os.Getenv("BinaryAppId"),
			RouterPortNo: conv_int("BinaryRouter"),
		},
		PubPortNo: conv_int("XsubPortNo"),
	}
	return binaryApi
}

func (b BinaryServer) setup(ch chan string) {

	c,_ := zmq.NewContext()
	req, _ := c.NewSocket(zmq.REQ)
	req.SetIdentity("req1")
	req.Connect(("tcp://localhost:"+strconv.Itoa(b.RouterPortNo)))
	defer req.Close()

	log.Println("connected to port.... pinging..")
	time.Sleep(2 * time.Second)
	for i := 0; i < 3; i++ {
	 	req.Send("Ready"+strconv.Itoa(i),0)
		log.Println("Sent ping message... receiving now")
		msd,_ := req.Recv(0)
		log.Println("Received message",msd)
	}
	log.Println("successfully pinged server...")

	ch <- "kill"
}

func TestBinaryInitialization(t *testing.T) {
	b := Init().Bs
	ws,_, _ := b.Dialer.Dial(b.Url,b.Header)

	c := make(chan string)
	go b.setup(c)
	go InitRouterServer(b,b.RouterPortNo,c,ws)

	if <-c == "kill"{
		log.Println("Test passed......")
	}
}

func TestWebsocketReturnsSuccess(t *testing.T){
	b := Init()
	_,err := b.Bs.InitializeWebsocket()
	if err != nil{
		t.Errorf("Websocket Test returned an error.....might be wrong ping/something")
	}
}

func TestTickDataReceived(t *testing.T){
	b := Init()

	ws,_ := b.Bs.InitializeWebsocket()

	log.Println("Starting the test.....")

	seed := Subscribe{
		Ticks:"R_50",
		Sub: 1,
	}

	byte_slice,_ := json.Marshal(seed)
	ws.WriteMessage(1,byte_slice)
	_,msg,_ := ws.ReadMessage()
	tick := TickStructure{}
	json.Unmarshal(msg,&tick)
	if tick.TickData.Symbol != "R_50"{
		t.Errorf("Sent data not received..... checking now..")
	}
}


