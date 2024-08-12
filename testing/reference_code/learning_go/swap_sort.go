package main

import "fmt"

func main() {
	var unsorted_array [50]int

	for n := range 50 {
		unsorted_array[n] = 50 - n
	}
	fmt.Println(unsorted_array)

	/*
		for n := range 49 {
			if unsorted_array[n] < unsorted_array[n+1] {
				temp := unsorted_array[n]
				unsorted_array[n] = unsorted_array[n+1]
				unsorted_array[n+1] = temp
				n = 0
			}
			unsorted_array[n] = 0
			fmt.Println(unsorted_array)
		}
	*/

	var index int = 0
	for index < 49 {
		if unsorted_array[index] > unsorted_array[index+1] {
			temp := unsorted_array[index]
			unsorted_array[index] = unsorted_array[index+1]
			unsorted_array[index+1] = temp
			index = 0
		} else {
			index += 1
		}
	}
	fmt.Println(unsorted_array)
}
