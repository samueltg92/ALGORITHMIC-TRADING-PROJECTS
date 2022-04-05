def fractals(df, High, Low, Up, Down):
    
    # fractal up
    for i in range(len(df)):
        if df[i, High] < df[i-2, High] and df[i-1, High] < df[i-2, High] and df[i-2, High] > df[i-3, High] and df[i-2, High] > df[i-4, High]:
            df[i-2, Up] = 1
            
            
    # fractal down
    for i in range(len(df)):
        if df[i, Low] > df[i-2, Low] and df[i-1, Low] > df[i-2, Low] and df[i-2, Low] < df[i-3, Low] and df[i-2, Low] < df[i-4, Low]:
            df[i-2, Down] = -1
            
    return df