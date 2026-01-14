load("irace_50.RData")
library(irace)
# Get summary data from the logfile.
irs <- irace_summarise(iraceResults)
# Get number of iterations
iters <- irs$n_iterations
# Get number of experiments (runs of target-runner) up to each iteration
fes <- cumsum(table(iraceResults$state$experiment_log[["iteration"]]))
# Get the mean value of all experiments executed up to each iteration
# for the best configuration of that iteration.
elites <- as.character(iraceResults$iterationElites)

x <- iraceResults$experiments[, elites, drop = FALSE]

values <- colMeans(x, na.rm = TRUE)

stderr <- function(v) {
  v <- v[is.finite(v)]
  if (length(v) <= 1) return(0)
  sqrt(var(v) / length(v))
}

err <- apply(x, 2, stderr)

low  <- values - err
high <- values + err
ok <- is.finite(low) & is.finite(high)

plot(fes[ok], values[ok], type = "s",
     xlab = "Number of runs of the target algorithm",
     ylab = "Mean value over testing set",
     ylim = c(min(low[ok]), max(high[ok])))

points(fes[ok], values[ok], pch = 19)
arrows(fes[ok], low[ok], fes[ok], high[ok], length = 0.05, angle = 90, code = 3)
text(fes[ok], values[ok], elites[ok], pos = 1)
