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
	Bs BinaryServer
	PubPortNo int
}

func main() {

	binary := BinaryApi{
		Bs: BinaryServer{
			Dialer: websocket.Dialer{},
			Header: http.Header{},
			Url: "wss://ws.binaryws.com/websockets/v3?app_id="+os.Getenv("BinaryAppId"),
			RouterPortNo: conv_int("BinaryRouter"),
		},
		PubPortNo: conv_int("XsubPortNo"),
	}
	binaryApi := binary.Bs
	ws, err := binaryApi.InitializeWebsocket()
	if err != nil{
		log.Fatal("Error opening connection to websocket..", err)
	}
	defer ws.Close()

	c := make(chan string)

	go binary.StartPubServer(c,ws)
	go InitRouterServer(binaryApi,binaryApi.RouterPortNo,c,ws)


	if <- c == "kill"{
		log.Fatal("Kill message received.... closing websocket and main routine")
	}
}

func (b BinaryApi) StartPubServer(ch chan string, ws *websocket.Conn) {
	c,_ := zmq.NewContext()
	p,_ := c.NewSocket(zmq.PUB)
	p.Connect("tcp://localhost:"+strconv.Itoa(b.PubPortNo))
	p.SetIdentity("pub1")

	defer p.Close()
	defer c.Term()
	
	for{
		_,msg,_ := ws.ReadMessage()
		tick := TickStructure{}
		json.Unmarshal(msg,&tick)

		s,b,a,e := tick.TickData.Symbol,
		           tick.TickData.Bid,
		           tick.TickData.Ask,
		           tick.TickData.Epoch
		p.Send(format(s,b,a,e),0)
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

func (m BinaryServer) ForLogic(
	ws *websocket.Conn,sock *zmq.Socket){

	for{
		log.Println("Receiving on router socket")
		msg, _ := sock.RecvMessage(0)
		tick := Subscribe{Sub:1}
		if msg[2] != ""{
			fmt.Println("message on router end",msg)
			*&tick.Ticks = msg[2]
			jso,_ := json.Marshal(tick)
			ws.WriteMessage(1,jso)
			sock.SendMessage([]string{msg[0],"","ok"})
			log.Println(msg[2])
		}
	}
	fmt.Println("Closing go routine")
}
