package main
import(
	"log"
	zmq "github.com/pebbe/zmq4"
	"testing"
	"strconv"
	"time"
	// "os"
)

const iters = 5

func TestXPubXSubConnection(t *testing.T) {

	b := XPubXSubInterMediary{
		XpubPortNo: 20000,
		XsubPortNo: 20008,
	}

	c := make(chan string)

	go b.SetUpSubClient(c)
	go b.SetUpPubServer(c)
	go b.Start(c)

	for i := 0; i < 2; i++ {
		log.Println("Loop",i)
		if <-c == "kill"{
			log.Println("Test passed......")
		}
	}
	log.Println("Tests successful....")
}



func (b XPubXSubInterMediary) SetUpPubServer(ch chan string) {

	c,_ := zmq.NewContext()
	pub, _ := c.NewSocket(zmq.PUB)
	pub.SetIdentity("pub1")
	pub.Connect("tcp://localhost:"+strconv.Itoa(b.XsubPortNo))
	defer pub.Unbind("tcp://localhost:"+strconv.Itoa(b.XsubPortNo))
	defer pub.Close()

	log.Println("Starting pub socket.....")
	for i := 0; i < iters; i++ {
		time.Sleep(2 * time.Second)
	 	pub.Send("hello Codex"+strconv.Itoa(i),0)
	}

	ch <- "kill"
}


func (b XPubXSubInterMediary) SetUpSubClient(ch chan string) {
	c,_ := zmq.NewContext()
	sub, _ := c.NewSocket(zmq.SUB)
	sub.SetIdentity("sub1")
	sub.SetSubscribe("")
	sub.Connect(("tcp://localhost:"+strconv.Itoa(b.XpubPortNo)))
	// sub.Set
	defer sub.Close()

	log.Println("Starting sub socket")
	for i := 0; i < iters; i++ {
	 	msg,_ := sub.Recv(0)
	 	log.Println("On sub side....",msg)
	}

	ch <- "kill"
}


