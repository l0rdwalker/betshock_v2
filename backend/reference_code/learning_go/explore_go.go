package main

import (
	"fmt"
)

const s string = "this is a test"

func main() {
	fmt.Printf(s)
	p := "\nsicko mode " + "epic"
	fmt.Printf(p)

	i := 55
	for i <= 100 {
		fmt.Println(i)
		if i == 60 {
			fmt.Println("\nThis is a number which we have hit.")
		}
		switch i {
		case 60:
			fmt.Println("We hit 60")
		case 65:
			fmt.Println("Sicko we've hit 65")
		case 70:
			fmt.Println("Ayo I think that we've hit 70")
		}
		i = i + 1
	}
}
