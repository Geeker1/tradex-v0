package main

import (
	zmq "github.com/pebbe/zmq4"
	"log"
	"strconv"
)

type XPubXSubInterMediary struct{
	XpubPortNo int
	XsubPortNo int
}

func main() {
	InterMediateServer := XPubXSubInterMediary{
		XpubPortNo: conv_int("XpubPortNo"),
		XsubPortNo: conv_int("XsubPortNo"),
	}

	c := make(chan string)
	go InterMediateServer.Start(c)

	if <-c == "kill"{
		log.Fatal("Kill message sent, shutting down xpub/xsub socket....")
	}
}




func (inter XPubXSubInterMediary) Start(ch chan string){
	log.Println("Starting xpub/xsub socket.....")
	ctx, _ := zmq.NewContext()
	xsub, _ := ctx.NewSocket(zmq.SUB)
	xpub, _ := ctx.NewSocket(zmq.XPUB)

	xsub.Bind("tcp://*:"+strconv.Itoa(inter.XsubPortNo))
	xsub.SetSubscribe("")
	xpub.Bind("tcp://*:"+strconv.Itoa(inter.XpubPortNo))
	
	poller := zmq.NewPoller()
	poller.Add(xsub, zmq.POLLIN)
	poller.Add(xpub, zmq.POLLIN)

	defer xsub.Close()
	defer xpub.Close()

	//  Process messages from both sockets
	for {
		// msg,_ := xsub.Recv(0)
		// xpub.Send(msg,0)
		// log.Println("Received message >>>",msg)
	    sockets, _ := poller.Poll(-1)
	    for _, socket := range sockets {
	        switch s := socket.Socket; s {
	        case xsub:
	            msg, _ := s.Recv(0)
	            log.Println("XSUB message :",msg)
	            xpub.Send(msg,0)
	        case xpub:
	            msg, _ := s.Recv(0)
	            log.Println("XPUB message",msg)
	        }
	    }
	}
}





