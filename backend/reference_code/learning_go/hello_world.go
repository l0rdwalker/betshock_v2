package main

import "fmt"

func main() {
	fmt.Println("Hello world")

	fmt.Println("go" + "lang")
	fmt.Println("1+1 = ", 1+1)
	fmt.Println(true && false)

	var a = "This is a test"
	fmt.Println(a)

	var z, b, c = 1, 2, 3

	fmt.Println(a, b, c, z)

	big_test := "very cool"
	very_cool_cool := 5.5

	fmt.Println(big_test, very_cool_cool)
}
