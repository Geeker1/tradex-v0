package main

import(
	"os"
	"strconv"
	"github.com/gorilla/websocket"
	"log"
	"encoding/json"
	"net/http"
	zmq "github.com/pebbe/zmq4"
	// "fmt"
)

type pio struct{
	Name string `json:"name"`
	No int `json:"no"`
}


// func main() {
// 	log.Println("Creating context and sockets")
// 	ctx,_ := zmq.NewContext()
// 	sock, _ := ctx.NewSocket(zmq.ROUTER)
// 	sock.Bind("tcp://*:45000")
// 	defer sock.Unbind("tcp://*:45000")
// 	defer sock.Close()
// 	defer ctx.Term()

// 	for {
// 		msg,_ := sock.RecvMessageBytes(0)
// 		sock.SendMessage(msg[0],"",msg[2])
// 	}
// }






// Defining binary api structs
type ping struct{
	Ping int `json:"ping"`
}

type PingResponse struct{
	Echo ping `json:"echo_req"`
	MsgType string `json:"msg_type"`
	Ping string `json:"ping"`
}

type Subscribe struct{
	Ticks string `json:"ticks"`
	Sub int `json:"subscribe"`
}

type SubId struct{
	Id string `json:"id"`
}

type Tick struct{
	Ask float64 `json:"ask"`
	Bid float64 `json:"bid"`
	Epoch float64 `json:"epoch"`
	Id string `json:"id"`
	Quote float64 `json:"quote"`
	Symbol string `json:"symbol"`
}

type TickStructure struct{
	Echo Subscribe `json:"echo_req"`
	MsgType string `json:"msg_type"`
	SubId string `json:"subscription"`
	TickData Tick `json:"tick"` 
}


func conv_int(value string) int {
	val,err := strconv.Atoi(os.Getenv(value))
	if err != nil{
		log.Fatal("Could not parse Env variable.....")
	}
	return val
}


// Below is the interface logic used to wrap the two binary servers on binary.com Api

type BinaryServer struct{
	Dialer websocket.Dialer
	Header http.Header
	Url string
	RouterPortNo int
}


// Any type that implements this function automatically uses this interface.....
type RouterServer interface{
	ForLogic(*websocket.Conn,*zmq.Socket)
}

// To initiate Main Router Server then pass the forloop logic...
func InitRouterServer(v RouterServer,p int,ch chan string,ws *websocket.Conn){ 
	c,_ := zmq.NewContext()
	r,_ := c.NewSocket(zmq.ROUTER)
	r.Bind("tcp://*:"+strconv.Itoa(p))

	defer r.Unbind(("tcp://*:"+strconv.Itoa(p)))
	defer r.Close()

	v.ForLogic(ws,r)

	ch <- "kill"
}


// Initialize Websocket and ping to server..., then exits
func (b BinaryServer) InitializeWebsocket()(*websocket.Conn, error) {
	ws,_, err := b.Dialer.Dial(
		b.Url,
		b.Header,
	)
	if err != nil{
		log.Println("Error Dialing websocket server: ",err)
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


