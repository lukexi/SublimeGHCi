import Control.Monad.Trans
import Control.Monad.State

> test3 = do
>     modify (+ 1)
>     lift $ modify (++ "1")
>     a <- get
>     b <- lift get
>     return (a,b)
test3

print "hi"
print "hi"

> let go3 = runIdentity $ evalStateT (evalStateT test3 0) "0"
> print 1
let x = 1
print x
let x = do 
    print "cheese"
    print "ham"
x

let y = do 
    print "cheese"
    print "ham"
y

data Poop = Poop Integer deriving Show