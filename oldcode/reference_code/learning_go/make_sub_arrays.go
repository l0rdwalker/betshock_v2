package main

import (
	"fmt"
	"math/rand/v2"
)

func main() {
	var array_length int = 5
	var outter_array = make([][]int, 5)
	fmt.Println(array_length)
	fmt.Println(outter_array)

	var index int = 0
	for index < array_length {
		outter_array[index] = make([]int, 25)
		for sub_index := 0; sub_index < 25; sub_index++ {
			outter_array[index][sub_index] = 25 - sub_index
		}
		index += 1
	}

	fmt.Println(outter_array)
	fmt.Println(rand.Float64())
	fmt.Println(rand.IntN(10), ",")
}
