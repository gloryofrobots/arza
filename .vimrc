augroup project
    autocmd!
    autocmd BufRead,BufNewFile *.h,*.c set filetype=c.doxygen
augroup END


let &path.="src/include,/usr/include/AL,"
"Djump through java imports
"set includeexpr=substitute(v:fname,'\\.','/','g')
set makeprg=make\ -C\ ../\ -j9

