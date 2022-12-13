const { Minesweeper } = require('../lib/minesweeper')

let game = new Minesweeper(8, 8, 8)
const [row, column] = Minesweeper.parseInput('de')

game.mine(row, column)
console.log(game.toString())
let canvas = game.drawPanel()
const fs = require('fs')
const out = fs.createWriteStream(__dirname + '/test.png')
const stream = canvas.createPNGStream()
stream.pipe(out)
out.on('finish', () => console.log('The PNG file was created.'))
console.log('create')
