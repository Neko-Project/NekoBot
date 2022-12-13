import { CanvasRenderingContext2D, createCanvas, registerFont } from 'canvas'

import path from 'path'
const COLUMN_NAME = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
registerFont(path.join(__dirname, '..', 'data', 'font', 'zpix.ttf'), {
  family: 'Zpix',
})

export class Minesweeper {
  board: Array<Array<Cell>>
  state: GameState
  row: number
  column: number
  mines: number
  action: number = 0
  size: [x: number, y: number]

  constructor(row: number, column: number, mines: number) {
    if (row > 26 || column > 26) throw new Error('暂不支持这么大的游戏盘')
    if (mines >= row * column || mines == 0) throw new Error('非法操作')
    if (mines < column - 1 || mines < row - 1)
      throw new Error('就不能来点难的吗')

    this.row = row
    this.column = column
    this.mines = mines
    this.state = GameState.PREPARE
    this.size = [row * 80, column * 80]

    // 创建 row x column 的棋盘数组
    this.board = new Array(row)
    for (let i = 0; i < row; i++) {
      this.board[i] = new Array(column)
      for (let j = 0; j < column; j++) {
        this.board[i][j] = new Cell(i, j)
      }
    }

    this.genMine()
  }

  drawPanel() {
    let canvas = createCanvas(this.size[0], this.size[1])
    let ctx = canvas.getContext('2d')
    ctx.fillStyle = 'white'
    ctx.fillRect(0, 0, this.size[0], this.size[1])
    this.drawGrid(ctx)
    this.drawCellCover(ctx)
    this.drawCell(ctx)
    return canvas
  }

  private drawGrid(ctx: CanvasRenderingContext2D) {
    for (const cell of [...this.rangeAllCells()]) {
      const { row, column } = cell
      ctx.strokeStyle = 'black'
      ctx.strokeRect(row * 80 + 7.5, column * 80 + 7.5, 65, 65)
    }
  }

  private drawCellCover(img: CanvasRenderingContext2D) {
    for (const cell of [...this.rangeAllCells()]) {
      const { row, column } = cell
      let fillStyle = img.fillStyle
      if (this.state == GameState.FAIL && cell.isBoom) {
        img.fillStyle = 'red'
      } else if (cell.isMarked) {
        img.fillStyle = 'blue'
      } else if (cell.isMined) {
        img.fillStyle = '#ccc'
      }
      img.fillRect(row * 80 + 8.5, column * 80 + 8.5, 63, 63)
      img.fillStyle = fillStyle
    }
  }

  private drawCell(img: CanvasRenderingContext2D) {
    img.fillStyle = 'black'
    img.font = '50px "Zpix"'
    for (const cell of [...this.rangeAllCells()]) {
      const { row, column } = cell
      if (!cell.isMined) {
        let index = `${COLUMN_NAME.charAt(row)}${COLUMN_NAME.charAt(column)}`
        img.fillText(index, 80 * row + 16, 80 * (column + 1) - 24)
      } else {
        let count = this.countAround(row, column)
        if (count == 0) {
          let fillStyle: string = img.fillStyle
          img.fillStyle = '#ccc'
          img.fillRect(row * 80 + 8.5, column * 80 + 8.5, 63, 63)
          img.fillStyle = fillStyle
          continue
        } else
          img.fillText(count.toString(), 80 * row + 34, 80 * (column + 1) - 24)
      }
      // img.fillText(cell.toString(), 80 * row + 34, 80 * (column + 1) - 24)
    }
  }

  private spreadNotMine(row: number, column: number) {
    if (!this.isValidLocation(row, column)) return
    const cell = this.board[row][column]

    if (cell.isChecked) return
    if (cell.isBoom) return

    cell.isMined = true
    cell.isChecked = true

    if (cell.count > 0) return
    for (var i = row - 1; i <= row + 1; i++) {
      for (var j = column - 1; j <= column + 1; j++) {
        if (i == row && j == column) continue
        this.spreadNotMine(i, j)
      }
    }
  }

  private resetCheck() {
    for (const cell of [...this.rangeAllCells()]) {
      cell.isChecked = false
    }
  }

  private winCheck() {
    let mined = 0
    for (const cell of [...this.rangeAllCells()]) {
      if (cell.isMined) mined += 1
      if (mined == this.row * this.column - this.mines) {
        this.state = GameState.WIN
      }
    }
  }

  private genMine() {
    // 随机放置地雷
    for (let i = 0; i < this.mines; i++) {
      // 获取随机的行列坐标
      let rrow = Math.floor(Math.random() * this.row)
      var rcol = Math.floor(Math.random() * this.column)
      // 如果当前格子已经有地雷，则重新随机
      while (this.board[rrow][rcol].isBoom) {
        rrow = Math.floor(Math.random() * this.row)
        rcol = Math.floor(Math.random() * this.column)
      }
      // 将地雷放置在当前格子中
      this.board[rrow][rcol].isBoom = true
    }
    for (const cell of [...this.rangeAllCells()]) {
      const { row, column } = cell
      cell.count = this.countAround(row, column)
    }
    this.state = GameState.GAMING
  }

  /**
   * 计算该格子周围 8 个格子中有多少个地雷
   * @param row
   * @param column
   */
  private countAround(row: number, column: number) {
    let count = 0
    for (var i = row - 1; i <= row + 1; i++) {
      for (var j = column - 1; j <= column + 1; j++) {
        // 跳过越界的格子
        if (!this.isValidLocation(i, j)) {
          continue
        }
        // 如果当前格子为地雷，则计数器加1
        if (this.board[i][j].isBoom) {
          count++
        }
      }
    }
    // 减去自身
    if (this.board[row][column].isBoom) {
      count -= 1
    }
    return count
  }

  private *rangeAllCells() {
    for (let i = 0; i < this.row; i++) {
      for (let j = 0; j < this.column; j++) {
        yield this.board[i][j]
      }
    }
  }

  private isValidLocation(row: number, column: number) {
    if (row >= this.row || column >= this.column || row < 0 || column < 0) {
      return false
    }
    return true
  }

  public mine(row: number, column: number) {
    if (!this.isValidLocation(row, column)) throw Error('非法操作')
    const cell = this.board[row][column]
    if (cell.isMined) throw Error('你已经挖过这里了')
    cell.isMined = true
    if (this.state != GameState.GAMING) throw Error('游戏已结束')
    this.action += 1
    if (cell.isBoom) {
      this.state = GameState.FAIL
      //throw Error(`挖到雷了！一共挖了 ${this.action} 次`)
    }
    this.resetCheck()
    this.spreadNotMine(row, column)
    this.winCheck()
  }

  public mark(row: number, column: number) {
    if (!this.isValidLocation(row, column)) throw Error('非法操作')
    const cell = this.board[row][column]
    if (cell.isMined) throw Error('你不能标记一个你挖开的地方')
    if (this.state != GameState.GAMING && this.state != GameState.PREPARE) {
      throw Error('游戏已结束')
    }
    if (cell.isMarked) cell.isMarked = false
    else cell.isMarked = true
  }

  public toString() {
    let str = ''
    for (const row of this.board) {
      str += row.join(' ') + '\n'
    }
    return str
  }

  public static parseInput(str: string) {
    if (str.length != 2) throw new Error('非法位置')
    return [
      COLUMN_NAME.indexOf(str.charAt(0).toUpperCase()),
      COLUMN_NAME.indexOf(str.charAt(1).toUpperCase()),
    ]
  }
}

class Cell {
  isBoom: boolean
  isMined: boolean
  isMarked: boolean
  isChecked = false
  row: number
  column: number
  count: number = 0
  constructor(
    row: number,
    column: number,
    isBoom = false,
    isMined = false,
    isMarked = false
  ) {
    this.row = row
    this.column = column
    this.isBoom = isBoom
    this.isMined = isMined
    this.isMarked = isMarked
  }

  getColor() {
    switch (this.count) {
      case 0:
        return '#483332'
      case 1:
        return '#15559a'
      case 2:
        return '#1ba784'
      case 3:
        return '#e2d849'
      default:
        break
    }
  }

  toString() {
    if (this.isBoom) return '*'
    return this.count.toString()
  }
}
export enum GameState {
  PREPARE,
  GAMING,
  WIN,
  FAIL,
}
