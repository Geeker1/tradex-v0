package main

import (
	zmq "github.com/pebbe/zmq4"
	"github.com/gorilla/websocket"
	"net/http"
	"encoding/json"
	"log"
	"fmt"
	"strconv"
	"os"
)

const delimiter = ";"

var flag zmq.Flag = 0
const prefix = "frx"

type BinaryApi struct{
	Dialer websocket.Dialer
	Header http.Header
	Url string
	PubPortNo,RouterPortNo int
}

func main() {

	binaryApi := BinaryApi{
		Dialer: websocket.Dialer{},
		Header: http.Header{},
		Url: "wss://ws.binaryws.com/websockets/v3?app_id="+os.Getenv("BinaryAppId"),
		PubPortNo: conv_int("XsubPortNo"),
		RouterPortNo: conv_int("RouterPortNo"),
	}

	fmt.Println(os.Getenv("BinaryAppId"))

	ws, err := binaryApi.InitializeWebsocket()
	if err != nil{
		log.Fatal("Error opening connection to websocket..", err)
	}
	defer ws.Close()

	c := make(chan string)

	// go binaryApi.RouterServeToApi(c,ws)
	// initialize pub here...
	// log.Println("Success : started all routines successfully...")

	go binaryApi.StartPubServer(c,ws)

	// Blocks main stream routine till a kill message s received from channel
	if <- c == "kill"{
		log.Fatal("Kill message received.... closing websocket and main routine")
	}

}

func format(s string,b float64,a float64,e float64) string {
	_new := 
	s+" "+strconv.FormatFloat(
		b,'e',-1,64)+delimiter+strconv.FormatFloat(
			a,'e',-1,64)+delimiter+strconv.FormatFloat(
				e,'e',-1,64)
	return _new
}

func (b BinaryApi) StartPubServer(ch chan string, ws *websocket.Conn) {
	c,_ := zmq.NewContext()
	p,_ := c.NewSocket(zmq.PUB)
	p.Connect("tcp://localhost:"+strconv.Itoa(b.PubPortNo))
	p.SetIdentity("pub1")

	defer p.Close()
	defer c.Term()

	seed := Subscribe{
		Ticks:"R_50",
		Sub: 1,
	}

	byte_slice,_ := json.Marshal(seed)
	ws.WriteMessage(1,byte_slice)
	for i := 0; i < 10; i++ {
		_,msg,_ := ws.ReadMessage()
		tick := TickStructure{}
		json.Unmarshal(msg,&tick)
		s,b,a,e := tick.TickData.Symbol,
		tick.TickData.Bid,
		tick.TickData.Ask,
		tick.TickData.Epoch
		p.Send(format(s,b,a,e),0)
	}
	
	ch <- "kill"
}


func (b BinaryApi) StartRouterServeToApi(ch chan string,ws *websocket.Conn) {

	c,_ := zmq.NewContext()
	r,_ := c.NewSocket(zmq.ROUTER)
	r.Bind("tcp://*:"+strconv.Itoa(b.RouterPortNo))

	defer r.Unbind(("tcp://*:"+strconv.Itoa(b.RouterPortNo)))
	defer r.Close()

	for{
		log.Println("Receiving on router socket")
		msg, _ := r.RecvMessage(0)
		if msg[2] != ""{
			fmt.Println("message on router end",msg)
			r.SendMessage([]string{msg[0],"","ok"})
		}
	}
	fmt.Println("Closing go routine")
}

func (b BinaryApi) InitializeWebsocket()(*websocket.Conn, error) {
	ws,_, err := b.Dialer.Dial(
		b.Url,
		b.Header,
	)
	if err != nil{
		log.Println("Error opening websocket connection to server: ",err)
		return nil, err
	}

	log.Println("Success : opened websocket connection")

	pinger := ping{
		Ping: 1,
	}
	BinaryResponse := PingResponse{}

	realo, _ := json.Marshal(pinger)
	ws.WriteMessage(1,realo)
	_,msg,_ := ws.ReadMessage()
	json.Unmarshal(msg,&BinaryResponse)

	if BinaryResponse.Ping == "pong"{
		log.Println("Success : pinged server")
	}

	return ws, nil
}



