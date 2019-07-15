package main

import "fmt"

type MetaTraderConnector struct{
	CLIENT_ID string
	host string
	protocol string
	PUSH_PORT int
	PULL_PORT int
	SUB_PORT int
	delimiter string
	verbose bool
	URL string
}

func main() {
	d := MetaTraderConnector{
		CLIENT_ID: "Darwin Labs",
	}

	fmt.Println(d.CLIENT_ID)

}

// func (m *MetaTraderConnector) INITIALS(){

// }


// func (m *MetaTraderConnector) SUBSCRIBE_MARKETDATA(symbol string, delimiter string){

// }

// func (m *MetaTraderConnector) UNSUBSCRIBE_MARKETDATA(symbol string){

// }

// func (m *MetaTraderConnector) UNSUBSCRIBE_ALL_MARKETDATA(){

// }

// func (m *MetaTraderConnector) DMX_POLL_DATA(){

// }


