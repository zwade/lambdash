let input = `return hidden.getFlag("if you can get this you deserve the flag -> abcd1234!@#$%^&*()'")`
//let input = "return Object.getOwnPropertyNames(global)";

let res = input.split("").map((c) => `cc(${c.charCodeAt(0)})`)

console.log(res.join(" + "));
