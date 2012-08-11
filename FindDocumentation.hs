import System.Process
import Data.List

ghcPkg args = fmap (last .words) $ readProcess "ghc-pkg" args []
replace item with = map (\x -> if x == item then with else x)
main = do
	let modName = "Graphics.Gloss"
	openDocsFor modName

openDocsFor modName = do
	let	docModName = replace '.' '-' modName
	packageName <- ghcPkg ["--simple-output", "find-module", modName]
	docPathRoot <- ghcPkg ["field", packageName, "haddock-html"]
	let modDocPath = docPathRoot ++ "/" ++ docModName ++ ".html"
	readProcess "open" [modDocPath] []