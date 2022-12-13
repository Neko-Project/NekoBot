import { Plugin, Option, logger } from 'kokkoro'
import { GameState, Minesweeper } from './minesweeper'
import { segment } from 'oicq'

const option: Option = {
  apply: true,
  lock: false,
}
const plugin = new Plugin('ms', option)

const gameDate = new Map<number, Minesweeper>()

plugin
  .command('start <x> <y> <mines>', 'group')
  .description('开始新游戏')
  .action(async (ctx) => {
    const { group_id, query } = ctx

    if (gameDate.has(group_id)) {
      ctx.reply('已经开始了')
      return
    }

    try {
      const { x, y, mines } = query
      let game = new Minesweeper(x, y, mines)
      gameDate.set(group_id, game)

      logger.debug('Generated:\n' + game.toString())

      let img = game.drawPanel()
      ctx.reply(['游戏开始了哦', segment.image(img.toBuffer())])
    } catch (err) {
      ctx.reply((<Error>err).message)
      gameDate.delete(group_id)
    }
  })

plugin
  .command('reset', 'group')
  .description('重置')
  .action((ctx) => {
    const { group_id } = ctx
    gameDate.delete(group_id)
    ctx.reply('已重置')
  })

plugin
  .command('mine <pos>', 'group')
  .description('挖掘一处方格')
  .action(async (ctx) => {
    const { group_id, query } = ctx
    let game = gameDate.get(group_id)

    if (!game) {
      ctx.reply('游戏未开始')
      return
    }

    try {
      const [row, column] = Minesweeper.parseInput(query.pos)
      logger.mark(`mined ${row} ${column}`)
      game.mine(row, column)
      let img = game.drawPanel()
      if (game.board[row][column].isBoom) {
        ctx.reply([
          `挖到雷了！\n一共挖了 ${game.action} 次`,
          segment.image(img.toBuffer()),
        ])
        gameDate.delete(group_id)
        return
      } else if (game.state == GameState.WIN) {
        ctx.reply(`你赢了！一共挖了 ${game.action} 次`)
      } else {
        ctx.reply(segment.image(img.toBuffer()))
      }
    } catch (error) {
      ctx.reply((<Error>error).message)
    }
  })

plugin
  .command('mark <pos>', 'group')
  .description('标记一处坐标')
  .action(async (ctx) => {
    const { group_id, query } = ctx
    let game = gameDate.get(group_id)

    if (!game) {
      ctx.reply('游戏未开始')
      return
    }

    try {
      const [row, column] = Minesweeper.parseInput(query.pos)
      logger.mark(`mined ${row} ${column}`)
      game.mark(row, column)
      let img = game.drawPanel()
      if (game.state == GameState.WIN) {
        ctx.reply(`你赢了！一共挖了 ${game.action} 次`)
      } else {
        ctx.reply(segment.image(img.toBuffer()))
      }
    } catch (error) {
      ctx.reply((<Error>error).message)
    }
  })
