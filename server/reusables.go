package main

import(
	"os"
	"strconv"
)

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
	val,_ := strconv.Atoi(os.Getenv(value))
	return val
}
















