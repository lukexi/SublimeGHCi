module FindDocumentation where
import System.Process
import Data.List
import System.FilePath ((</>))

openDocsFor :: [Char] -> IO String
openDocsFor modName = do
	let	docModName = replace '.' '-' modName
	packageName <- runGhcPkg ["--simple-output", "find-module", modName]
	docPathRoot <- runGhcPkg ["field", packageName, "haddock-html"]
	let modDocPath = docPathRoot </> docModName ++ ".html"
	readProcess "open" [modDocPath] []
	where
		replace :: Eq b => b -> b -> [b] -> [b]
		replace item with = map (\x -> if x == item then with else x)
		runGhcPkg :: [String] -> IO String
		runGhcPkg args = fmap (last .words) $ readProcess "ghc-pkg" args []

--main = do
--	let modName = "Graphics.Gloss"
--	openDocsFor modName