package main

import (
	"fmt"
	"math/rand/v2"
)

func min(a int, b int) int {
	if a > b {
		return a
	}
	return b
}

func merge_sort(array []int) []int {
	if len(array) == 2 {
		if array[0] > array[1] {
			var temp int = array[0]
			array[0] = array[1]
			array[1] = temp
		}
	} else if len(array) > 1 {
		var pivot int = int(len(array) / 2)

		lhs := make([]int, pivot)
		copy(lhs[:], array[0:pivot])
		lhs = merge_sort(lhs)

		rhs := make([]int, len(array)-pivot)
		copy(rhs[:], array[pivot:len(array)])
		rhs = merge_sort(rhs)

		idx := 0
		rhs_idx := 0
		lhs_idx := 0
		for idx = 0; idx < len(array); idx++ {
			if lhs_idx == len(lhs) {
				array[idx] = rhs[rhs_idx]
				rhs_idx += 1
				continue
			} else if rhs_idx == len(rhs) {
				array[idx] = lhs[lhs_idx]
				lhs_idx += 1
				continue
			}

			if lhs[lhs_idx] < rhs[rhs_idx] {
				array[idx] = lhs[lhs_idx]
				lhs_idx += 1
			} else {
				array[idx] = rhs[rhs_idx]
				rhs_idx += 1
			}
		}
	}

	return array
}

func construct_arrays(array_length int, sub_array_length int) [][]int {
	new_array := make([][]int, array_length)
	for index := 0; index < array_length; index++ {
		sub_array := make([]int, sub_array_length)
		for sub_index := 0; sub_index < sub_array_length; sub_index++ {
			sub_array[sub_index] = rand.IntN(100)
		}
		new_array[index] = sub_array
		new_array[index] = merge_sort(new_array[index])
	}

	return new_array
}

func main() {
	var array_length int = 15
	test_array := construct_arrays(array_length, 15)
	fmt.Println(test_array)
}
