-- Convert a number to a list of its digits
digits :: Int -> [Int]
digits n = map (\x -> read [x] :: Int) $ show n

-- Square and return an Int rather than a float like (**)
square :: Int -> Int
square n = n * n

-- Run the happy number algorithm: sum the square of the digits
hChain :: Int -> Int
hChain n = foldl1 (+) (map square $ digits n)

-- Find a happy number. Happy if we hit 1, sad if we hit the following infinite loop:
--   42 -> 20 -> 4 -> 16 -> 37 -> 58 -> 89 -> 145 -> 42 ...
happy :: Int -> Bool
happy 1  = True
happy 42 = False  -- Example failure case of the infinite loop
happy n  = happy $ hChain n

-- Find the happy numbers up to n
happyToN :: Int -> [Int]
happyToN n = filter happy [1..n]

-- Find the ratio of happy numbers to sad number up to n
happyProp :: Int -> Float
happyProp n = fromIntegral (length $ happyToN n) / fromIntegral n
