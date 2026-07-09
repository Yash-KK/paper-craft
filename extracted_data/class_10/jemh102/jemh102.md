[Figure 1](images/page_1_image_1.md)

1062CH02

# POLYNOMIALS

# 2

## 2.1 Introduction

In Class IX, you have studied polynomials in one variable and their degrees. Recall that if $p(x)$ is a polynomial in $x$, the highest power of $x$ in $p(x)$ is called **the degree of the polynomial** $p(x)$. For example, $4x + 2$ is a polynomial in the variable $x$ of degree 1, $2y^2 - 3y + 4$ is a polynomial in the variable $y$ of degree 2, $5x^3 - 4x^2 + x - \sqrt{2}$ is a polynomial in the variable $x$ of degree 3 and $7u^6 - \frac{3}{2}u^4 + 4u^2 + u - 8$ is a polynomial in the variable $u$ of degree 6. Expressions like $\frac{1}{x-1}$, $\sqrt{x} + 2$, $\frac{1}{x^2 + 2x + 3}$ etc., are not polynomials.

A polynomial of degree 1 is called a **linear polynomial**. For example, $2x - 3$, $\sqrt{3}x + 5$, $y + \sqrt{2}$, $x - \frac{2}{11}$, $3z + 4$, $\frac{2}{3}u + 1$, etc., are all linear polynomials. Polynomials such as $2x + 5 - x^2$, $x^3 + 1$, etc., are not linear polynomials.

A polynomial of degree 2 is called a **quadratic polynomial**. The name ‘quadratic’ has been derived from the word ‘quadrate’, which means ‘square’. $2x^2 + 3x - \frac{2}{5}$, $y^2 - 2$, $2 - x^2 + \sqrt{3}x$, $\frac{u}{3} - 2u^2 + 5$, $\sqrt{5}v^2 - \frac{2}{3}v$, $4z^2 + \frac{1}{7}$ are some examples of quadratic polynomials (whose coefficients are real numbers). More generally, any quadratic polynomial in $x$ is of the form $ax^2 + bx + c$, where $a, b, c$ are real numbers and $a \neq 0$. A polynomial of degree 3 is called a **cubic polynomial**. Some examples of

Reprint 2026-27

<!-- page break -->

POLYNOMIALS

11

a cubic polynomial are $2 - x^3$, $x^3$, $\sqrt{2}x^3$, $3 - x^2 + x^3$, $3x^3 - 2x^2 + x - 1$. In fact, the most general form of a cubic polynomial is

$$ax^3 + bx^2 + cx + d,$$

where, $a, b, c, d$ are real numbers and $a \neq 0$.

Now consider the polynomial $p(x) = x^2 - 3x - 4$. Then, putting $x = 2$ in the polynomial, we get $p(2) = 2^2 - 3 \times 2 - 4 = -6$. The value $-6$, obtained by replacing $x$ by 2 in $x^2 - 3x - 4$, is the value of $x^2 - 3x - 4$ at $x = 2$. Similarly, $p(0)$ is the value of $p(x)$ at $x = 0$, which is $-4$.

If $p(x)$ is a polynomial in $x$, and if $k$ is any real number, then the value obtained by replacing $x$ by $k$ in $p(x)$, is called **the value of $p(x)$ at $x = k$**, and is denoted by $p(k)$.

What is the value of $p(x) = x^2 - 3x - 4$ at $x = -1$? We have :

$$p(-1) = (-1)^2 - \{3 \times (-1)\} - 4 = 0$$

Also, note that $p(4) = 4^2 - (3 \times 4) - 4 = 0$.

As $p(-1) = 0$ and $p(4) = 0$, $-1$ and $4$ are called the zeroes of the quadratic polynomial $x^2 - 3x - 4$. More generally, a real number $k$ is said to be a **zero of a polynomial $p(x)$**, if $p(k) = 0$.

You have already studied in Class IX, how to find the zeroes of a linear polynomial. For example, if $k$ is a zero of $p(x) = 2x + 3$, then $p(k) = 0$ gives us $2k + 3 = 0$, i.e., $k = -\frac{3}{2}$.

In general, if $k$ is a zero of $p(x) = ax + b$, then $p(k) = ak + b = 0$, i.e., $k = \frac{-b}{a}$.

So, the zero of the linear polynomial $ax + b$ is $\frac{-b}{a} = \frac{-(\text{Constant term})}{\text{Coefficient of } x}$.

Thus, the zero of a linear polynomial is related to its coefficients. Does this happen in the case of other polynomials too? For example, are the zeroes of a quadratic polynomial also related to its coefficients?

In this chapter, we will try to answer these questions. We will also study the division algorithm for polynomials.

## 2.2 Geometrical Meaning of the Zeroes of a Polynomial

You know that a real number $k$ is a zero of the polynomial $p(x)$ if $p(k) = 0$. But why are the zeroes of a polynomial so important? To answer this, first we will see the **geometrical** representations of linear and quadratic polynomials and the geometrical meaning of their zeroes.

Reprint 2026-27

<!-- page break -->

12

MATHEMATICS

Consider first a linear polynomial $ax + b, a \neq 0$. You have studied in Class IX that the graph of $y = ax + b$ is a straight line. For example, the graph of $y = 2x + 3$ is a straight line passing through the points $(-2, -1)$ and $(2, 7)$.

[tbl-0.md](tables/page_3_table_1.md)

From Fig. 2.1, you can see that the graph of $y = 2x + 3$ intersects the $x$-axis mid-way between $x = -1$ and $x = -2$, that is, at the point $\left(-\frac{3}{2}, 0\right)$.

You also know that the zero of $2x + 3$ is $-\frac{3}{2}$. Thus, the zero of the polynomial $2x + 3$ is the $x$-coordinate of the point where the graph of $y = 2x + 3$ intersects the $x$-axis.

[Figure 1](images/page_3_image_1.md)

Fig. 2.1

In general, for a linear polynomial $ax + b, a \neq 0$, the graph of $y = ax + b$ is a straight line which intersects the $x$-axis at exactly one point, namely, $\left(-\frac{b}{a}, 0\right)$. Therefore, the linear polynomial $ax + b, a \neq 0$, has exactly one zero, namely, the $x$-coordinate of the point where the graph of $y = ax + b$ intersects the $x$-axis.

Now, let us look for the geometrical meaning of a zero of a quadratic polynomial. Consider the quadratic polynomial $x^2 - 3x - 4$. Let us see what the graph* of $y = x^2 - 3x - 4$ looks like. Let us list a few values of $y = x^2 - 3x - 4$ corresponding to a few values for $x$ as given in Table 2.1.

* Plotting of graphs of quadratic or cubic polynomials is not meant to be done by the students, nor is to be evaluated.

Reprint 2026-27

<!-- page break -->

POLYNOMIALS

13

Table 2.1

[tbl-1.md](tables/page_4_table_1.md)

If we locate the points listed above on a graph paper and draw the graph, it will actually look like the one given in Fig. 2.2.

In fact, for any quadratic polynomial $ax^2 + bx + c, a \neq 0$, the graph of the corresponding equation $y = ax^2 + bx + c$ has one of the two shapes either open upwards like $\bigcup$ or open downwards like $\bigcap$ depending on whether $a > 0$ or $a < 0$. (These curves are called **parabolas**.)

You can see from Table 2.1 that -1 and 4 are zeroes of the quadratic polynomial. Also note from Fig. 2.2 that -1 and 4 are the $x$-coordinates of the points where the graph of $y = x^2 - 3x - 4$ intersects the $x$-axis. Thus, the zeroes of the quadratic polynomial $x^2 - 3x - 4$ are $x$-coordinates of the points where the graph of $y = x^2 - 3x - 4$ intersects the $x$-axis.

This fact is true for any quadratic polynomial, i.e., the zeroes of a quadratic polynomial $ax^2 + bx + c, a \neq 0$, are precisely the $x$-coordinates of the points where the parabola representing $y = ax^2 + bx + c$ intersects the $x$-axis.

From our observation earlier about the shape of the graph of $y = ax^2 + bx + c$, the following three cases can happen:

[Figure 1](images/page_4_image_1.md)

Fig. 2.2

Reprint 2026-27

<!-- page break -->

14

MATHEMATICS

**Case (i) :** Here, the graph cuts $x$-axis at two distinct points A and A'.

The $x$-coordinates of A and A' are the **two zeroes** of the quadratic polynomial $ax^2 + bx + c$ in this case (see Fig. 2.3).

[Figure 1](images/page_5_image_1.md)

Fig. 2.3

**Case (ii) :** Here, the graph cuts the $x$-axis at exactly one point, i.e., at two coincident points. So, the two points A and A' of Case (i) coincide here to become one point A (see Fig. 2.4).

[Figure 2](images/page_5_image_2.md)

Fig. 2.4

The $x$-coordinate of A is the **only zero** for the quadratic polynomial $ax^2 + bx + c$ in this case.

Reprint 2026-27

<!-- page break -->

POLYNOMIALS

15

**Case (iii) :** Here, the graph is either completely above the $x$-axis or completely below the $x$-axis. So, it does not cut the $x$-axis at any point (see Fig. 2.5).

[Figure 1](images/page_6_image_1.md)

**Fig. 2.5**

So, the quadratic polynomial $ax^2 + bx + c$ has **no zero** in this case.

So, you can see geometrically that a quadratic polynomial can have either two distinct zeroes or two equal zeroes (i.e., one zero), or no zero. This also means that a polynomial of degree 2 has almost two zeroes.

Now, what do you expect the geometrical meaning of the zeroes of a cubic polynomial to be? Let us find out. Consider the cubic polynomial $x^3 - 4x$. To see what the graph of $y = x^3 - 4x$ looks like, let us list a few values of $y$ corresponding to a few values for $x$ as shown in Table 2.2.

**Table 2.2**

[tbl-2.md](tables/page_6_table_1.md)

Locating the points of the table on a graph paper and drawing the graph, we see that the graph of $y = x^3 - 4x$ actually looks like the one given in Fig. 2.6.

Reprint 2026-27

<!-- page break -->

16

MATHEMATICS

We see from the table above that $-2$, $0$ and $2$ are zeroes of the cubic polynomial $x^3 - 4x$. Observe that $-2$, $0$ and $2$ are, in fact, the $x$-coordinates of the only points where the graph of $y = x^3 - 4x$ intersects the $x$-axis. Since the curve meets the $x$-axis in only these 3 points, their $x$-coordinates are the only zeroes of the polynomial.

Let us take a few more examples. Consider the cubic polynomials $x^3$ and $x^3 - x^2$. We draw the graphs of $y = x^3$ and $y = x^3 - x^2$ in Fig. 2.7 and Fig. 2.8 respectively.

[Figure 1](images/page_7_image_1.md)

Fig. 2.6

[Figure 2](images/page_7_image_2.md)

Fig. 2.7

[Figure 3](images/page_7_image_3.md)

Fig. 2.8

Reprint 2026-27

<!-- page break -->

POLYNOMIALS

17

Note that 0 is the only zero of the polynomial $x^3$. Also, from Fig. 2.7, you can see that 0 is the $x$-coordinate of the only point where the graph of $y = x^3$ intersects the $x$-axis. Similarly, since $x^3 - x^2 = x^2(x - 1)$, 0 and 1 are the only zeroes of the polynomial $x^3 - x^2$. Also, from Fig. 2.8, these values are the $x$-coordinates of the only points where the graph of $y = x^3 - x^2$ intersects the $x$-axis.

From the examples above, we see that there are at most 3 zeroes for any cubic polynomial. In other words, any polynomial of degree 3 can have at most three zeroes.

**Remark :** In general, given a polynomial $p(x)$ of degree $n$, the graph of $y = p(x)$ intersects the $x$-axis at at most $n$ points. Therefore, a polynomial $p(x)$ of degree $n$ has at most $n$ zeroes.

**Example 1 :** Look at the graphs in Fig. 2.9 given below. Each is the graph of $y = p(x)$, where $p(x)$ is a polynomial. For each of the graphs, find the number of zeroes of $p(x)$.

[Figure 1](images/page_8_image_1.md)

Fig. 2.9

**Solution :**

- (i) The number of zeroes is 1 as the graph intersects the $x$-axis at one point only.
- (ii) The number of zeroes is 2 as the graph intersects the $x$-axis at two points.
- (iii) The number of zeroes is 3. (Why?)

Reprint 2026-27

<!-- page break -->

18

MATHEMATICS

- (iv) The number of zeroes is 1. (Why?)
- (v) The number of zeroes is 1. (Why?)
- (vi) The number of zeroes is 4. (Why?)

### EXERCISE 2.1

1. The graphs of $y = p(x)$ are given in Fig. 2.10 below, for some polynomials $p(x)$. Find the number of zeroes of $p(x)$, in each case.

[Figure 1](images/page_9_image_1.md)

Fig. 2.10

### 2.3 Relationship between Zeroes and Coefficients of a Polynomial

You have already seen that zero of a linear polynomial $ax + b$ is $-\frac{b}{a}$. We will now try to answer the question raised in Section 2.1 regarding the relationship between zeroes and coefficients of a quadratic polynomial. For this, let us take a quadratic polynomial, say $p(x) = 2x^2 - 8x + 6$. In Class IX, you have learnt how to factorise quadratic polynomials by splitting the middle term. So, here we need to split the middle term ‘$-8x$’ as a sum of two terms, whose product is $6 \times 2x^2 = 12x^2$. So, we write

$$\begin{aligned} 2x^2 - 8x + 6 &= 2x^2 - 6x - 2x + 6 = 2x(x - 3) - 2(x - 3) \\ &= (2x - 2)(x - 3) = 2(x - 1)(x - 3) \end{aligned}$$

Reprint 2026-27

<!-- page break -->

POLYNOMIALS

19

So, the value of $p(x) = 2x^2 - 8x + 6$ is zero when $x - 1 = 0$ or $x - 3 = 0$, i.e., when $x = 1$ or $x = 3$. So, the zeroes of $2x^2 - 8x + 6$ are 1 and 3. Observe that :

$$\text{Sum of its zeroes} = 1 + 3 = 4 = \frac{-(-8)}{2} = \frac{-(\text{Coefficient of } x)}{\text{Coefficient of } x^2}$$

$$\text{Product of its zeroes} = 1 \times 3 = 3 = \frac{6}{2} = \frac{\text{Constant term}}{\text{Coefficient of } x^2}$$

Let us take one more quadratic polynomial, say, $p(x) = 3x^2 + 5x - 2$. By the method of splitting the middle term,

$$\begin{aligned} 3x^2 + 5x - 2 &= 3x^2 + 6x - x - 2 = 3x(x + 2) - 1(x + 2) \\ &= (3x - 1)(x + 2) \end{aligned}$$

Hence, the value of $3x^2 + 5x - 2$ is zero when either $3x - 1 = 0$ or $x + 2 = 0$, i.e., when $x = \frac{1}{3}$ or $x = -2$. So, the zeroes of $3x^2 + 5x - 2$ are $\frac{1}{3}$ and $-2$. Observe that :

$$\text{Sum of its zeroes} = \frac{1}{3} + (-2) = \frac{-5}{3} = \frac{-(\text{Coefficient of } x)}{\text{Coefficient of } x^2}$$

$$\text{Product of its zeroes} = \frac{1}{3} \times (-2) = \frac{-2}{3} = \frac{\text{Constant term}}{\text{Coefficient of } x^2}$$

In general, if $\alpha^*$ and $\beta^*$ are the zeroes of the quadratic polynomial $p(x) = ax^2 + bx + c$, $a \neq 0$, then you know that $x - \alpha$ and $x - \beta$ are the factors of $p(x)$. Therefore,

$$\begin{aligned} ax^2 + bx + c &= k(x - \alpha)(x - \beta), \text{ where } k \text{ is a constant} \\ &= k[x^2 - (\alpha + \beta)x + \alpha\beta] \\ &= kx^2 - k(\alpha + \beta)x + k\alpha\beta \end{aligned}$$

Comparing the coefficients of $x^2$, $x$ and constant terms on both the sides, we get

$$a = k, b = -k(\alpha + \beta) \text{ and } c = k\alpha\beta.$$

This gives

$$\alpha + \beta = \frac{-b}{a},$$

$$\alpha\beta = \frac{c}{a}$$

* $\alpha, \beta$ are Greek letters pronounced as 'alpha' and 'beta' respectively. We will use later one more letter '$\gamma$' pronounced as 'gamma'.

Reprint 2026-27

<!-- page break -->

20

MATHEMATICS

$$\text{sum of zeroes} = \alpha + \beta = -\frac{b}{a} = \frac{-(\text{Coefficient of } x)}{\text{Coefficient of } x^2},$$

$$\text{product of zeroes} = \alpha\beta = \frac{c}{a} = \frac{\text{Constant term}}{\text{Coefficient of } x^2}.$$

Let us consider some examples.

**Example 2 :** Find the zeroes of the quadratic polynomial $x^2 + 7x + 10$, and verify the relationship between the zeroes and the coefficients.

**Solution :** We have

$$x^2 + 7x + 10 = (x + 2)(x + 5)$$

So, the value of $x^2 + 7x + 10$ is zero when $x + 2 = 0$ or $x + 5 = 0$, i.e., when $x = -2$ or $x = -5$. Therefore, the zeroes of $x^2 + 7x + 10$ are $-2$ and $-5$. Now,

$$\text{sum of zeroes} = -2 + (-5) = -(7) = \frac{-(7)}{1} = \frac{-(\text{Coefficient of } x)}{\text{Coefficient of } x^2},$$

$$\text{product of zeroes} = (-2) \times (-5) = 10 = \frac{10}{1} = \frac{\text{Constant term}}{\text{Coefficient of } x^2}.$$

**Example 3 :** Find the zeroes of the polynomial $x^2 - 3$ and verify the relationship between the zeroes and the coefficients.

**Solution :** Recall the identity $a^2 - b^2 = (a - b)(a + b)$. Using it, we can write:

$$x^2 - 3 = (x - \sqrt{3})(x + \sqrt{3})$$

So, the value of $x^2 - 3$ is zero when $x = \sqrt{3}$ or $x = -\sqrt{3}$.

Therefore, the zeroes of $x^2 - 3$ are $\sqrt{3}$ and $-\sqrt{3}$.

Now,

$$\text{sum of zeroes} = \sqrt{3} - \sqrt{3} = 0 = \frac{-(\text{Coefficient of } x)}{\text{Coefficient of } x^2},$$

$$\text{product of zeroes} = (\sqrt{3})(-\sqrt{3}) = -3 = \frac{-3}{1} = \frac{\text{Constant term}}{\text{Coefficient of } x^2}.$$

Reprint 2026-27

<!-- page break -->

POLYNOMIALS

21

**Example 4 :** Find a quadratic polynomial, the sum and product of whose zeroes are $-3$ and $2$, respectively.

**Solution :** Let the quadratic polynomial be $ax^2 + bx + c$, and its zeroes be $\alpha$ and $\beta$. We have

$$\alpha + \beta = -3 = \frac{-b}{a},$$

and

If $a = 1$, then $b = 3$ and $c = 2$.

So, one quadratic polynomial which fits the given conditions is $x^2 + 3x + 2$.

You can check that any other quadratic polynomial that fits these conditions will be of the form $k(x^2 + 3x + 2)$, where $k$ is real.

Let us now look at cubic polynomials. Do you think a similar relation holds between the zeroes of a cubic polynomial and its coefficients?

Let us consider $p(x) = 2x^3 - 5x^2 - 14x + 8$.

You can check that $p(x) = 0$ for $x = 4, -2, \frac{1}{2}$. Since $p(x)$ can have at most three zeroes, these are the zeroes of $2x^3 - 5x^2 - 14x + 8$. Now,

$$\text{sum of the zeroes} = 4 + (-2) + \frac{1}{2} = \frac{5}{2} = \frac{-(-5)}{2} = \frac{-(\text{Coefficient of } x^2)}{\text{Coefficient of } x^3},$$

$$\text{product of the zeroes} = 4 \times (-2) \times \frac{1}{2} = -4 = \frac{-8}{2} = \frac{-\text{Constant term}}{\text{Coefficient of } x^3}.$$

However, there is one more relationship here. Consider the sum of the products of the zeroes taken two at a time. We have

$$\begin{aligned} \{4 \times (-2)\} + \{(-2) \times \frac{1}{2}\} + \{\frac{1}{2} \times 4\} \\ = -8 - 1 + 2 = -7 = \frac{-14}{2} = \frac{\text{Coefficient of } x}{\text{Coefficient of } x^3}. \end{aligned}$$

In general, it can be proved that if $\alpha, \beta, \gamma$ are the zeroes of the cubic polynomial $ax^3 + bx^2 + cx + d$, then

Reprint 2026-27

<!-- page break -->

22

MATHEMATICS

$$\begin{aligned}\alpha + \beta + \gamma &= \frac{-b}{a}, \\ \alpha\beta + \beta\gamma + \gamma\alpha &= \frac{c}{a}, \\ \alpha\beta\gamma &= \frac{-d}{a}.\end{aligned}$$

Let us consider an example.

**Example 5\*** : Verify that $3, -1, -\frac{1}{3}$ are the zeroes of the cubic polynomial $p(x) = 3x^3 - 5x^2 - 11x - 3$, and then verify the relationship between the zeroes and the coefficients.

**Solution :** Comparing the given polynomial with $ax^3 + bx^2 + cx + d$, we get

$a = 3, b = -5, c = -11, d = -3$. Further

$$p(3) = 3 \times 3^3 - (5 \times 3^2) - (11 \times 3) - 3 = 81 - 45 - 33 - 3 = 0,$$

$$p(-1) = 3 \times (-1)^3 - 5 \times (-1)^2 - 11 \times (-1) - 3 = -3 - 5 + 11 - 3 = 0,$$

$$\begin{aligned}p\left(-\frac{1}{3}\right) &= 3 \times \left(-\frac{1}{3}\right)^3 - 5 \times \left(-\frac{1}{3}\right)^2 - 11 \times \left(-\frac{1}{3}\right) - 3, \\ &= -\frac{1}{9} - \frac{5}{9} + \frac{11}{3} - 3 = -\frac{2}{3} + \frac{2}{3} = 0\end{aligned}$$

Therefore, $3, -1$ and $-\frac{1}{3}$ are the zeroes of $3x^3 - 5x^2 - 11x - 3$.

So, we take $\alpha = 3, \beta = -1$ and $\gamma = -\frac{1}{3}$.

Now,

$$\alpha + \beta + \gamma = 3 + (-1) + \left(-\frac{1}{3}\right) = 2 - \frac{1}{3} = \frac{5}{3} = \frac{-(-5)}{3} = \frac{-b}{a},$$

$$\alpha\beta + \beta\gamma + \gamma\alpha = 3 \times (-1) + (-1) \times \left(-\frac{1}{3}\right) + \left(-\frac{1}{3}\right) \times 3 = -3 + \frac{1}{3} - 1 = \frac{-11}{3} = \frac{c}{a},$$

$$\alpha\beta\gamma = 3 \times (-1) \times \left(-\frac{1}{3}\right) = 1 = \frac{-(-3)}{3} = \frac{-d}{a}.$$

\* Not from the examination point of view.

Reprint 2026-27

<!-- page break -->

POLYNOMIALS

23

## EXERCISE 2.2

1. Find the zeroes of the following quadratic polynomials and verify the relationship between the zeroes and the coefficients.

(i)  $x^2 - 2x - 8$

(ii)  $4s^2 - 4s + 1$

(iii)  $6x^2 - 3 - 7x$

(iv)  $4u^2 + 8u$

(v)  $t^2 - 15$

(vi)  $3x^2 - x - 4$

2. Find a quadratic polynomial each with the given numbers as the sum and product of its zeroes respectively.

(i)  $\frac{1}{4}, -1$

(ii)  $\sqrt{2}, \frac{1}{3}$

(iii)  $0, \sqrt{5}$

(iv) 1, 1

(v)  $-\frac{1}{4}, \frac{1}{4}$

(vi) 4, 1

## 2.4 Summary

In this chapter, you have studied the following points:

1. Polynomials of degrees 1, 2 and 3 are called linear, quadratic and cubic polynomials respectively.
2. A quadratic polynomial in $x$ with real coefficients is of the form $ax^2 + bx + c$, where $a, b, c$ are real numbers with $a \neq 0$.
3. The zeroes of a polynomial $p(x)$ are precisely the $x$-coordinates of the points, where the graph of $y = p(x)$ intersects the $x$-axis.
4. A quadratic polynomial can have at most 2 zeroes and a cubic polynomial can have at most 3 zeroes.
5. If $\alpha$ and $\beta$ are the zeroes of the quadratic polynomial $ax^2 + bx + c$, then

$$\alpha + \beta = -\frac{b}{a}, \quad \alpha\beta = \frac{c}{a}.$$

6. If $\alpha, \beta, \gamma$ are the zeroes of the cubic polynomial $ax^3 + bx^2 + cx + d$, then

$$\alpha + \beta + \gamma = \frac{-b}{a},$$

$$\alpha\beta + \beta\gamma + \gamma\alpha = \frac{c}{a},$$

and  $\alpha\beta\gamma = \frac{-d}{a}$.

Reprint 2026-27
