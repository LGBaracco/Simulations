setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
getwd()

dataset <- read.table("PepperedMoths_experiment.csv",
                      sep    = ',',
                      skip   = 6,
                      header = TRUE)

pollution <- dataset$pollution
blackness <- dataset$averageBlackness


shapiro.test(pollution)
shapiro.test(blackness)


plot(pollution, blackness,
     ylim = c(0, 100),
     xlim = c(0, 90),
     xlab = "Pollution",
     ylab = "Average blackness")

lines(lowess(pollution, blackness), col = "black")


testResult <- cor.test(pollution, 
                       blackness, 
                       alternative = "greater",
                       method = "spearman",
                       exact = FALSE)

testResult
