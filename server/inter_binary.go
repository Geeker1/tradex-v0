package main

import (
	zmq "github.com/pebbe/zmq4"
	"log"
	"strconv"
	"os"
	"time"
)

func main() {
	c := make(chan string)
	go RouterSocket(c)
	time.Sleep(2 * time.Second)
	for i := 0; i < 2; i++ {
		go ReqSock(c,i)
	}
	
	for i := 0; i < 2; i++ {
		msgo := <- c
		log.Println(msgo)
	}
	os.Exit(1)
}


func ReqSock(ch chan string,it int) {
	ctx, _ := zmq.NewContext()
	sock, _ := ctx.NewSocket(zmq.REQ)
	sock.SetIdentity("sock"+strconv.Itoa(it))
	sock.Connect("ipc://codex.ipc")

	defer sock.Close()
	defer ctx.Term()

	time.Sleep(2 * time.Second)
	sock.Send("socket"+strconv.Itoa(it)+" hi"+strconv.Itoa(1),0)
	mk,_ := sock.Recv(0)
	log.Println("Request received..","loop",1,mk)
	ch <- "kill"
}

func RouterSocket(ch chan string) {
	ctx, _ := zmq.NewContext()
	sock, _ := ctx.NewSocket(zmq.ROUTER)
	sock.Bind("ipc://codex.ipc")

	defer sock.Close()
	defer ctx.Term()

	for{
		msg, _ := sock.RecvMessage(0)
		log.Println("RouterSocket received.....",msg)
		sock.SendMessage(msg,0)
	}
}


