package main

import (
  "flag"
  "runtime"
  "fmt"
)

func main() {
  cpunum := flag.Int("cpunum", 0, "cpunum")
  flag.Parse()
  fmt.Println("cpunum:", *cpunum)
  runtime.GOMAXPROCS(*cpunum)
  for i := 0; i < *cpunum - 1; i++ {
    go func() {
      for {

      }
    }()
  }
  for {

  }
}