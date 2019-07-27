package main

import (
	"log"

	"github.com/gorilla/websocket"
	zmq "github.com/pebbe/zmq4"

	// "strconv"
	"os"
	// "time"
	"fmt"
	"net/http"
	"time"
	// "encoding/json"
)

type InterMedServer BinaryServer

func main() {

	inter := BinaryServer{
		Dialer:       websocket.Dialer{},
		Header:       http.Header{},
		Url:          "wss://ws.binaryws.com/websockets/v3?app_id=" + os.Getenv("BinaryAppId"),
		RouterPortNo: conv_int("InterRouterNo"),
	}

	fmt.Println(inter.Url, inter.RouterPortNo)

	ws, err := inter.InitializeWebsocket()
	if err != nil {
		log.Fatal("Error pinging websocket..... Restart script..")
	}

	ws.SetPongHandler(setLoop)

	log.Println("Websocket connection opened.......")
	ch := make(chan string)

	go pingWeb(ws)
	go InitRouterServer(inter, inter.RouterPortNo, ch, ws)

	if <-ch == "kill" {
		log.Println(
			"kill message sent from Router on Intermediate Code Server",
			"\nExiting Program",
		)
	}
}

func setLoop(appData string) error {
	log.Println("Pong Message Received...", appData)
	return nil
}

func pingWeb(ws *websocket.Conn) {
	log.Println("Started pong web loop handler")
	for {
		time.Sleep(10 * time.Second)
		err := ws.WriteMessage(9, []byte("pong_message"))
		if err != nil {
			log.Fatal("Error pinging ...", err)
		}
	}
}

func (m BinaryServer) ForLogic(
	ws *websocket.Conn, sock *zmq.Socket) {

	log.Println("Receiving on Inter router socket")

	for {
		msg, E := sock.RecvMessageBytes(0)
		if E != nil {
			log.Println("Error reading from InterRouterSocket")
		}
		log.Println("Received message from Router Socket")

		Werr := ws.WriteMessage(1, msg[2])
		if Werr != nil {
			log.Println("Error writing normal message")
		}
		log.Println("Sent message through Websocket")

		t, m, e := ws.ReadMessage()
		if e != nil {
			log.Println("Error reading message from connection")
		}
		log.Println("Received new websocket message with type of", t)

		sock.SendMessage(msg[0], "", m)
	}
}
