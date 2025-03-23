from flask import Blueprint, render_template, request
import sympy as sp

inversa_bp = Blueprint('inversa', __name__)

@inversa_bp.route('/inversa', methods=['GET', 'POST'])
def inversa():
    resultado = ""
    procedimiento = []
    transformadas_utilizadas = set()

    if request.method == 'POST':
        try:
            funcion_input = request.form['expresion']
            
            t, s = sp.symbols('t s')
            F_s = sp.sympify(funcion_input)

            procedimiento.append("<h3>Paso 1: Función Original en el dominio S</h3>")
            procedimiento.append("<p>Se tiene la función en el dominio de \\( s \\):</p>")
            procedimiento.append(f"<p>$$ F(s) = {sp.latex(F_s)} $$</p>")

            procedimiento.append("<h3>Paso 2: Propiedades de la Transformada Inversa de Laplace</h3>")

            for term in F_s.as_ordered_terms():
                numerador, denominador = term.as_numer_denom()

                if denominador == s:
                    A = numerador
                    transformadas_utilizadas.add(
                        f"$$ \\mathcal{{L}}^{{-1}} \\left\\{{ \\frac{{{sp.latex(A)}}}{{s}} \\right\\}} = {sp.latex(A)} $$"
                    )

                elif denominador.is_Pow and denominador.base == s and denominador.exp < 0:
                    n = abs(denominador.exp) - 1
                    transformadas_utilizadas.add(
                        f"$$ \\mathcal{{L}}^{{-1}} \\left\\{{ \\frac{{{n}!}}{{s^{{{n+1}}}}} \\right\\}} = t^{{{n}}} $$"
                    )

                elif denominador.is_Add and len(denominador.args) == 2 and s in denominador.args:
                    a_valor = -denominador.args[1] if denominador.args[0] == s else -denominador.args[0]
                    transformadas_utilizadas.add(
                        f"$$ \\mathcal{{L}}^{{-1}} \\left\\{{ \\frac{{1}}{{s - {sp.latex(a_valor)}}} \\right\\}} = e^{{{sp.latex(a_valor)} t}} $$"
                    )

                elif denominador.is_Pow and denominador.base.is_Add and len(denominador.base.args) == 2:
                    if denominador.base.args[0] == s**2:
                        a_valor = sp.sqrt(denominador.base.args[1])
                        if numerador == s:
                            transformadas_utilizadas.add(
                                f"$$ \\mathcal{{L}}^{{-1}} \\left\\{{ \\frac{{s}}{{s^2 + {sp.latex(a_valor)}^2}} \\right\\}} = \\cos({sp.latex(a_valor)} t) $$"
                            )
                        elif numerador == a_valor:
                            transformadas_utilizadas.add(
                                f"$$ \\mathcal{{L}}^{{-1}} \\left\\{{ \\frac{{{sp.latex(a_valor)}}}{{s^2 + {sp.latex(a_valor)}^2}} \\right\\}} = \\sin({sp.latex(a_valor)} t) $$"
                            )

            if transformadas_utilizadas:
                procedimiento.append("<p>En este caso, aplicamos las siguientes reglas:</p>")
                for formula in transformadas_utilizadas:
                    procedimiento.append(f"<strong>{formula}</strong>")
            else:
                procedimiento.append("<p>Aplicamos la Transformada Inversa de Laplace directamente.</p>")

            procedimiento.append("<h3>Paso 3: Aplicación de la Transformada Inversa</h3>")

            inversa_total = sp.inverse_laplace_transform(F_s, s, t)
            inversa_total = inversa_total.subs(sp.Heaviside(t), 1)

            if F_s.is_Add:
                terminos = F_s.as_ordered_terms()
                transformadas_parciales = [sp.inverse_laplace_transform(term, s, t) for term in terminos]
                
                for i, term in enumerate(terminos):
                    procedimiento.append(f"<p><strong>Para el término:</strong> $$ {sp.latex(term)} $$</p>")
                    procedimiento.append("<p>Aplicamos la transformada inversa:</p>")
                    procedimiento.append(f"<p>$$ \\mathcal{{L}}^{{-1}} \\left\\{{ {sp.latex(term)} \\right\\}} = {sp.latex(transformadas_parciales[i])} $$</p>")

            else:
                procedimiento.append("<p>Aplicamos la Transformada Inversa directamente:</p>")
                procedimiento.append(f"<p>$$ \\mathcal{{L}}^{{-1}} \\left\\{{ {sp.latex(F_s)} \\right\\}} = {sp.latex(inversa_total)} $$</p>")

            procedimiento.append("<h3>Paso 4: Resultado Final</h3>")
            procedimiento.append("<p>La Transformada Inversa de Laplace completa es:</p>")
            resultado = sp.latex(inversa_total)
            procedimiento.append(f"<p>$$ f(t) = {resultado} $$</p>")

        except Exception as e:
            procedimiento.append("<p><strong>Error:</strong> La función ingresada no es válida. Verifica la sintaxis.</p>")
            resultado = ""

    procedimiento_html = "".join(procedimiento)

    return render_template('inversa.html', resultado=resultado, procedimiento=procedimiento_html)
