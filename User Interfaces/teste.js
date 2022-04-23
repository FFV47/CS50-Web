class Animal {
	speak() {
		return this;
	}
	static eat() {
		return this;
	}
}

let obj = new Animal();
obj.speak(); // the Animal object
console.log(obj.speak());
let speak = obj.speak;
speak(); // undefined

Animal.eat(); // class Animal
console.log(Animal.eat());
let eat = Animal.eat;
eat(); // undefined
