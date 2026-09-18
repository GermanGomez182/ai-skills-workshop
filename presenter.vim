" Presenter mode for WORKSHOP.md: one section on screen at a time.
"
"   nvim -S presenter.vim WORKSHOP.md
"
" Space   next section (previous one folds shut, new one opens at the top)
" Backspace   previous section
" zo / zc   open / close the section under the cursor by hand
"
" Sections are the [NN] markers. Everything else stays folded, so the
" audience never sees two sections at once, whatever the pane height.

" --- chrome off: nothing on screen but the talk ---------------------
set noruler noshowcmd noshowmode
set noswapfile shortmess+=A

" Your own config would otherwise show through: statusline, indent
" guides. All silent, so this still works on a bare nvim.
silent! lua pcall(function() require('lualine').hide() end)
silent! IBLDisable
autocmd VimEnter,BufWinEnter,WinEnter * set laststatus=0
set nonumber norelativenumber signcolumn=no
set scrolloff=0 sidescrolloff=0
let &fillchars = 'fold: ,eob: '
set nowrap
set colorcolumn=

" --- fold one level per [NN] section --------------------------------
function! PresenterFold(lnum) abort
  return getline(a:lnum) =~# '^\[\d\d\]' ? '>1' : '1'
endfunction

setlocal foldmethod=expr
setlocal foldexpr=PresenterFold(v:lnum)
setlocal foldminlines=0

" A closed section shows just its title, indented like a chapter list.
function! PresenterFoldText() abort
  let l:line = substitute(getline(v:foldstart), '\s*$', '', '')
  return l:line =~# '^\[\d\d\]' ? '   ' . l:line : '   AI SKILLS WORKSHOP'
endfunction
setlocal foldtext=PresenterFoldText()

" --- moving between sections ----------------------------------------
function! s:Section(dir) abort
  normal! zM
  if a:dir > 0
    call search('^\[\d\d\]', 'W')
  else
    call search('^\[\d\d\]', 'bW')
  endif
  normal! zv
  normal! zt
endfunction

nnoremap <silent> <Space> :call <SID>Section(1)<CR>
nnoremap <silent> <BS> :call <SID>Section(-1)<CR>
nnoremap <silent> <Home> :call <SID>Section(-1)<CR>

" Start closed, on the title screen.
normal! zM
normal! gg
