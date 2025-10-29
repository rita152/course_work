![](_page_0_Picture_0.jpeg)

## CHAPTER 13

# **Financial Applications**

In this chapter, we shall study some applications of linear programming to problems in quantitative finance.

## **1. Portfolio Selection**

Every investor, from the individual to the professional fund manager, must decide on an appropriate mix of assets to include in his or her investment portfolio. Given a collection of potential investments (indexed, say, from 1 to n), let R<sup>j</sup> denote the return in the next time period on investment j, j = 1,...,n. In general, R<sup>j</sup> is a random variable, although some investments may be essentially deterministic.

A *portfolio* is determined by specifying what fraction of one's assets to put into each investment. That is, a portfolio is a collection of nonnegative numbers x<sup>j</sup> , j = 1,...,n, that sum to one. The return (on each dollar) one would obtain using a given portfolio is given by

$$R = \sum_{j} x_{j} R_{j}.$$

The *reward* associated with such a portfolio is defined as the expected return1 :

$$\mathbb{E}R = \sum_{j} x_{j} \mathbb{E}R_{j}.$$

If reward were the only issue, then the problem would be trivial: simply put everything in the investment with the highest expected return. But unfortunately, investments with high reward typically also carry a high level of risk. That is, even though they are expected to do very well in the long run, they also tend to be erratic in the short term. There are many ways to define risk, some better than others. We will define the *risk*

$$\mathbb{E}R = \frac{1}{T} \sum_{t=1}^{T} R(t).$$

<sup>1</sup> In this chapter, we assume a modest familiarity with the ideas and notations of probability: the symbol E denotes *expected value*, which means that, if R is a *random variable* that takes values R(1), R(2),...,R(T) with equal probability, then

<span id="page-1-0"></span>associated with an investment (or, for that matter, a portfolio of investments) to be the *mean absolute deviation from the mean (MAD)*:

$$\mathbb{E}|R - \mathbb{E}R| = \mathbb{E}\left|\sum_{j} x_{j}(R_{j} - \mathbb{E}R_{j})\right|$$
$$= \mathbb{E}\left|\sum_{j} x_{j}\tilde{R}_{j}\right|,$$

where  $\tilde{R}_j = R_j - \mathbb{E} R_j$ . One would like to maximize the reward while at the same time not incur excessive risk. Whenever confronted with two (or more) competing objectives, it is necessary to consider a spectrum of possible optimal solutions as one moves from putting most weight on one objective to the other. In our portfolio selection problem, we form a linear combination of the reward and the risk (parametrized here by  $\mu$ ) and maximize that:

(13.1) 
$$\max \min_{j} x_{j} \mathbb{E}R_{j} - \mathbb{E}\left|\sum_{j} x_{j} \tilde{R}_{j}\right|$$
 subject to 
$$\sum_{j} x_{j} = 1$$
 
$$x_{j} \geq 0 \qquad j = 1, 2, \dots, n.$$

Here,  $\mu$  is a positive parameter that represents the importance of risk relative to reward: high values of  $\mu$  tend to maximize reward regardless of risk, whereas low values attempt to minimize risk.

It is important to note that by diversifying (that is, not putting everything into one investment), it might be possible to reduce the risk without reducing the reward. To see how this can happen, consider a hypothetical situation involving two investments A and B. Each year, investment A either goes up 30 % or goes down 10 %, but unfortunately, the ups and downs are unpredictable (that is, each year is independent of the previous years and is an up year with probability 1/2). Investment B is also highly volatile. In fact, in any year in which A goes up 30 %, investment B goes down 10 %, and in the years in which A goes down 10 %, B goes up 30 %. Clearly, by putting half of our portfolio into A and half into B, we can create a portfolio that goes up 10% every year without fail. The act of identifying investments that are negatively correlated with each other (such as A and B) and dividing the portfolio among these investments is called hedging. Unfortunately, it is fairly difficult to find pairs of investments with strong negative correlations. But such negative correlations do occur. Generally speaking, they can be expected to occur when the fortunes of both A and B depend on a common underlying factor. For example, a hot, rainless summer is good for energy but bad for agriculture.

<span id="page-2-0"></span>

| Year-   | SHY   | XLB       | XLE    | XLF       | XLI     | XLK   | XLP     | XLU   | XLV    |
|---------|-------|-----------|--------|-----------|---------|-------|---------|-------|--------|
| Month   | Bonds | Materials | Energy | Financial | Indust. | Tech. | Staples | Util. | Health |
| 2007-04 | 1.000 | 1.044     | 1.068  | 1.016     | 1.035   | 1.032 | 1.004   | 0.987 | 1.014  |
| 2007-03 | 1.003 | 1.015     | 1.051  | 1.039     | 1.046   | 1.047 | 1.028   | 1.049 | 1.073  |
| 2007-02 | 1.005 | 1.024     | 1.062  | 0.994     | 1.008   | 1.010 | 1.021   | 1.036 | 1.002  |
| 2007-01 | 1.007 | 1.027     | 0.980  | 0.971     | 0.989   | 0.973 | 0.985   | 1.053 | 0.977  |
| 2006-12 | 1.002 | 1.040     | 0.991  | 1.009     | 1.021   | 1.020 | 1.020   | 0.996 | 1.030  |
| 2006-11 | 1.001 | 0.995     | 0.969  | 1.030     | 0.997   | 0.989 | 1.020   | 0.999 | 1.007  |
| 2006-10 | 1.005 | 1.044     | 1.086  | 1.007     | 1.024   | 1.028 | 0.991   | 1.026 | 0.999  |
| 2006-09 | 1.004 | 1.060     | 1.043  | 1.023     | 1.028   | 1.040 | 1.018   | 1.053 | 1.003  |
| 2006-08 | 1.004 | 1.000     | 0.963  | 1.040     | 1.038   | 1.040 | 0.999   | 0.985 | 1.015  |
| 2006-07 | 1.008 | 1.030     | 0.949  | 1.012     | 1.011   | 1.070 | 1.039   | 1.028 | 1.029  |
| 2006-06 | 1.007 | 0.963     | 1.034  | 1.023     | 0.943   | 0.974 | 1.016   | 1.048 | 1.055  |
| 2006-05 | 1.002 | 1.005     | 1.022  | 0.995     | 0.999   | 0.995 | 1.018   | 1.023 | 1.000  |
| 2006-04 | 1.002 | 0.960     | 0.972  | 0.962     | 0.983   | 0.935 | 1.002   | 1.016 | 0.979  |
| 2006-03 | 1.002 | 1.035     | 1.050  | 1.043     | 1.021   | 0.987 | 1.010   | 1.016 | 0.969  |
| 2006-02 | 1.002 | 1.047     | 1.042  | 1.003     | 1.044   | 1.023 | 1.008   | 0.954 | 0.987  |
| 2006-01 | 1.000 | 0.978     | 0.908  | 1.021     | 1.031   | 1.002 | 1.008   | 1.013 | 1.012  |
| 2005-12 | 1.002 | 1.048     | 1.146  | 1.009     | 1.003   | 1.034 | 1.002   | 1.024 | 1.013  |
| 2005-11 | 1.004 | 1.029     | 1.018  | 1.000     | 1.005   | 0.969 | 1.001   | 1.009 | 1.035  |
| 2005-10 | 1.004 | 1.076     | 1.015  | 1.048     | 1.058   | 1.063 | 1.009   | 0.999 | 1.012  |
| 2005-09 | 0.999 | 1.002     | 0.909  | 1.030     | 0.986   | 0.977 | 0.996   | 0.936 | 0.969  |
| 2005-08 | 0.997 | 1.008     | 1.063  | 1.009     | 1.017   | 1.002 | 1.014   | 1.042 | 0.995  |
| 2005-07 | 1.007 | 0.958     | 1.064  | 0.983     | 0.976   | 0.991 | 0.983   | 1.006 | 0.996  |
| 2005-06 | 0.996 | 1.056     | 1.071  | 1.016     | 1.038   | 1.057 | 1.032   | 1.023 | 1.023  |
| 2005-05 | 1.002 | 0.980     | 1.070  | 1.012     | 0.974   | 0.987 | 0.981   | 1.059 | 0.994  |

TABLE 13.1. Monthly returns per dollar for each of nine investments over 2 years. That is, \$1 invested in the energy sector fund XLE on April 1, 2007, was worth \$1.068 on April 30, 2007.

Solving problem [\(13.1\)](#page-1-0) requires knowledge of the joint distribution of the R<sup>j</sup> 's. However, this distribution is not known theoretically but instead must be estimated by looking at historical data. For example, Table 13.1 shows monthly returns over a recent 2-year period for one bond fund (3-year Treasury Bonds) and eight different sector index funds: Materials (XLB), Energy (XLE), Financial (XLF), Industrial (XLI), Technology (XLK), Staples (XLP), Utilities (XLU), and Healthcare (XLV). Let R<sup>j</sup> (t) denote the return on investment j over T monthly time periods as shown in Table 13.1. One way to estimate the mean ER<sup>j</sup> is simply to take the average of the historical returns:

$$\mathbb{E}R_j = \frac{1}{T} \sum_{t=1}^T R_j(t).$$

<span id="page-3-0"></span>**1.1. Reduction to a Linear Programming Problem.** As formulated, the problem in (13.1) is not a linear programming problem. We use the same trick we used in the previous chapter to replace each absolute value with a new variable and then impose inequality constraints that ensure that the new variable will indeed be the appropriate absolute value once an optimal value to the problem has been obtained. But first, let us rewrite (13.1) with the expected value operation replaced by a simple averaging over the given historical data:

(13.2) 
$$\max \min z \quad \mu \sum_{j} x_{j} r_{j} - \frac{1}{T} \sum_{t=1}^{T} \left| \sum_{j} x_{j} (R_{j}(t) - r_{j}) \right|$$
 subject to 
$$\sum_{j} x_{j} = 1$$
 
$$x_{j} \geq 0 \qquad j = 1, 2, \dots, n,$$

where

$$r_j = \frac{1}{T} \sum_{t=1}^{T} R_j(t)$$

denotes the expected reward for asset j. Now, replace  $\left|\sum_j x_j (R_j(t) - r_j)\right|$  with a new variable  $y_t$  and rewrite the optimization problem as

(13.3) 
$$\max \min z \quad \mu \sum_{j} x_{j} r_{j} - \frac{1}{T} \sum_{t=1}^{T} y_{t}$$
 subject to 
$$-y_{t} \leq \sum_{j} x_{j} (R_{j}(t) - r_{j}) \leq y_{t} \qquad t = 1, 2, \dots, T,$$
 
$$\sum_{j} x_{j} = 1$$
 
$$x_{j} \geq 0 \qquad j = 1, 2, \dots, n$$
 
$$y_{t} > 0 \qquad t = 1, 2, \dots, T.$$

As we have seen in other contexts before, at optimality one of the two inequalities involving  $y_t$  must actually be an equality because if both inequalities were strict, then it would be possible to further increase the objective function by reducing  $y_t$ .

1.2. Solution via Parametric Simplex Method. The problem formulation given by (13.3) is a linear program that can be solved for any particular value of  $\mu$  using the methods described in previous chapters. However, we can do much better than this. The problem is a parametric linear programming problem, where the parameter is the risk aversion parameter  $\mu$ . If we can give a value of  $\mu$  for which a basic optimal solution is obvious, then we can start from this basic solution and use the parametric simplex method to find the optimal solution associated with each and every value of  $\mu$ . It is easy to see that for  $\mu$  larger than some threshold, the optimal solution is to put

all of our portfolio into a single asset, the one with the highest expected reward  $r_j$ . Let  $j^*$  denote this highest reward asset:

$$r_{i^*} \ge r_i$$
 for all  $j$ .

We need to write (13.3) in dictionary form. To this end, let us introduce slack variables  $w_t^+$  and  $w_t^-$ :

$$\begin{aligned} \text{maximize} \quad & \mu \sum_{j} x_{j} r_{j} - \frac{1}{T} \sum_{t=1}^{T} y_{t} \\ \text{subject to} \quad & -y_{t} - \sum_{j} x_{j} (R_{j}(t) - r_{j}) + w_{t}^{-} = 0 \qquad t = 1, 2, \dots, T, \\ & -y_{t} + \sum_{j} x_{j} (R_{j}(t) - r_{j}) + w_{t}^{+} = 0 \qquad t = 1, 2, \dots, T, \\ & \sum_{j} x_{j} = 1 \\ & x_{j} \geq 0 \qquad j = 1, 2, \dots, n, \\ & y_{t}, w_{t}^{+}, w_{t}^{-} \geq 0 \qquad t = 1, 2, \dots, T. \end{aligned}$$

We have 3T+n nonnegative variables and 2T+1 equality constraints. Hence, we need to find 2T+1 basic variables and T+n-1 nonbasic variables. Since we know the optimal values for each of the allocation variables,  $x_{j^*}=1$  and the rest of the  $x_j$ 's vanish, it is straightforward to figure out the values of the other variables as well. We can then simply declare any variable that is positive to be basic and declare the rest to be nonbasic. With this prescription, the variable  $x_{j^*}$  must be basic. The remaining  $x_j$ 's are nonbasic. Similarly, all of the  $y_t$ 's are nonzero and hence basic. For each t, either  $w_t^-$  or  $w_t^+$  is basic and the other is nonbasic. To say which is which, we need to introduce some additional notation. Let

$$D_{tj} = R_j(t) - r_j.$$

Then it is easy to check that  $w_t^-$  is basic if  $D_{tj^*} > 0$  and  $w_t^+$  is basic if  $D_{tj^*} < 0$  (the unlikely case where  $D_{tj^*} = 0$  can be decided arbitrarily). Let

$$T^+ = \{t : D_{tj^*} > 0\}$$
 and  $T^- = \{t : D_{tj^*} < 0\}$ 

and let

$$\epsilon_t = \begin{cases} 1, \text{ for } t \in T^+\\ -1, \text{ for } t \in T^-. \end{cases}$$

It is tedious, but here is the optimal dictionary:

$$\zeta = \frac{1}{T} \sum_{t=1}^{T} \epsilon_{t} D_{tj^{*}} - \frac{1}{T} \sum_{j \neq j^{*}} \sum_{t=1}^{T} \epsilon_{t} (D_{tj} - D_{tj^{*}}) x_{j} - \frac{1}{T} \sum_{t \in T^{-}} w_{t}^{-} - \frac{1}{T} \sum_{t \in T^{+}} w_{t}^{+}$$

$$+ \mu r_{j^{*}} + \mu \sum_{j \neq j^{*}} (r_{j} - r_{j^{*}}) x_{j}$$

$$y_{t} = -D_{tj^{*}} - \sum_{j \neq j^{*}} (D_{tj} - D_{tj^{*}}) x_{j} + w_{t}^{-} \qquad t \in T^{-}$$

$$w_{t}^{-} = 2 D_{tj^{*}} + 2 \sum_{j \neq j^{*}} (D_{tj} - D_{tj^{*}}) x_{j} + w_{t}^{+} \qquad t \in T^{+}$$

$$y_{t} = D_{tj^{*}} + \sum_{j \neq j^{*}} (D_{tj} - D_{tj^{*}}) x_{j} + w_{t}^{+} \qquad t \in T^{+}$$

$$w_{t}^{+} = -2 D_{tj^{*}} - 2 \sum_{j \neq j^{*}} (D_{tj} - D_{tj^{*}}) x_{j} + w_{t}^{-} \qquad t \in T^{-}$$

$$x_{j^{*}} = 1 - \sum_{j \neq j^{*}} x_{j}.$$

We can now check that, for large  $\mu$ , this dictionary is optimal. Indeed, the objective coefficients on the  $w_t^-$  and  $w_t^+$  variables in the first row of the objective function are negative. The coefficients on the  $x_j$ 's in the first row can be positive or negative but for  $\mu$  sufficiently large, the negative coefficients on the  $x_j$ 's in the second row dominate and make all coefficients negative after considering both rows. Similarly, the fact that all of the basic variables are positive follows immediately from the definitions of  $T^+$  and  $T^-$ .

A few simple inequalities determine the  $\mu$ -threshold above which the given dictionary is optimal. The parametric simplex method can then be used to systematically reduce  $\mu$  to zero. Along the way, each dictionary encountered corresponds to an optimal solution for some range of  $\mu$  values. Hence, in one pass we have solved the portfolio selection problem for every investor from the bravest to the most cautious. Figure 13.1 shows all of the optimal portfolios. The set of all risk–reward profiles that are possible is shown in Figure 13.2. The lower-right boundary of this set is the so-called *efficient frontier*. Any portfolio that produces a risk–reward combination that does not lie on the efficient frontier can be improved either by increasing its mean reward without changing the risk or by decreasing the risk without changing the mean reward. Hence, one should only invest in portfolios that lie on the efficient frontier.

