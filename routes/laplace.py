from flask import Blueprint, render_template, request
import sympy as sp

laplace_bp = Blueprint('laplace', __name__)
@laplace_bp.route('/', methods=['GET', 'POST'])
def index():
    resultado = ""
    procedimiento = []
    transformadas_utilizadas = set()

    if request.method == 'POST':
        try:
            funcion_input = request.form['expresion']
            
            t, s = sp.symbols('t s')
            f_t = sp.sympify(funcion_input)

            def expandir_cos2(expr):
                """Reemplaza solo los términos que sean exactamente cos^2(at), sin afectar otros."""
                return expr.replace(
                    lambda x: isinstance(x, sp.Pow) and x.base.func == sp.cos and x.exp == 2,
                    lambda x: (1 + sp.cos(2 * x.base.args[0])) / 2
                )

            if any(isinstance(term, sp.Pow) and term.base.func == sp.cos and term.exp == 2 for term in f_t.atoms(sp.Pow)):
                f_t_expanded = expandir_cos2(f_t)
            else:
                f_t_expanded = f_t

            procedimiento.append("<h3>Paso 1: Función Original</h3>")
            procedimiento.append(f"Se tiene la función:<br>")
            procedimiento.append(f"$$ f(t) = {sp.latex(f_t)} $$")

            if f_t != f_t_expanded:
                procedimiento.append("<h3>Expansión de Identidades Trigonométricas</h3>")
                procedimiento.append("Se aplica la identidad trigonométrica con los valores específicos:<br>")

                for term in f_t.atoms(sp.Pow):
                    if term.base.func == sp.cos and term.exp == 2:
                        a_value = term.base.args[0]
                        identidad_trigonometrica = rf"$$ \cos^2({sp.latex(a_value)}) = \frac{{1 + \cos({sp.latex(2*a_value)})}}{2} $$"
                        procedimiento.append(identidad_trigonometrica)

                procedimiento.append(f"Después de la conversión:<br>")
                procedimiento.append(f"$$ f(t) = {sp.latex(f_t_expanded)} $$")

            f_t = f_t_expanded

            procedimiento.append("<h3>Paso 2: Propiedades de la Transformada de Laplace Utilizadas</h3>")

            if f_t.has(sp.sin):
                transformadas_utilizadas.add(r"$$ \mathcal{L}\{ \sin(at) \} = \frac{a}{s^2 + a^2} $$")
            if f_t.has(sp.cos):
                transformadas_utilizadas.add(r"$$ \mathcal{L}\{ \cos(at) \} = \frac{s}{s^2 + a^2} $$")
            if f_t.has(sp.exp):
                transformadas_utilizadas.add(r"$$ \mathcal{L}\{ e^{-at} \} = \frac{1}{s + a} $$")
            if any(
                (isinstance(term, sp.Pow) and term.base == t) or term == t
                for term in f_t.atoms(sp.Basic)
            ):
                transformadas_utilizadas.add(r"$$ \mathcal{L}\{ t^n \} = \frac{n!}{s^{n+1}} $$")
            if f_t.has(sp.Heaviside):
                transformadas_utilizadas.add(r"$$ \mathcal{L}\{ H(t-a)f(t-a) \} = e^{-as}F(s) $$")

            if transformadas_utilizadas:
                for formula in transformadas_utilizadas:
                    procedimiento.append(formula)
            else:
                procedimiento.append("No se detectaron reglas específicas, se aplicará la Transformada de Laplace directamente.")

            procedimiento.append("<h3>Paso 3: Aplicación de la Transformada de Laplace</h3>")

            transformada_total = sp.laplace_transform(f_t, t, s, noconds=True)

            if f_t.is_Add:
                terminos = f_t.as_ordered_terms()
                transformadas_parciales = [sp.laplace_transform(term, t, s, noconds=True) for term in terminos]
                
                for i, term in enumerate(terminos):
                    procedimiento.append(rf"<p><strong>Para el término: </strong> $$ {sp.latex(term)} $$</p>")
                    procedimiento.append(rf"<p>$$ \mathcal{{L}}\{{ {sp.latex(term)} \}} = {sp.latex(transformadas_parciales[i])} $$</p>")

            else:
                procedimiento.append("Aplicando la Transformada de Laplace directamente:")
                procedimiento.append(rf"$$ \mathcal{{L}}\{{ {sp.latex(f_t)} \}} = {sp.latex(transformada_total)} $$")

            procedimiento.append("<h3>Paso 4: Resultado Final</h3>")
            procedimiento.append("La Transformada de Laplace completa es:<br>")
            resultado = sp.latex(transformada_total)
            procedimiento.append(f"$$ F(s) = {resultado} $$")

        except Exception as e:
            procedimiento.append("<strong>Error:</strong> La función ingresada no es válida. Verifica la sintaxis.")
            resultado = ""

    procedimiento_html = "".join(procedimiento)

    return render_template('index.html', resultado=resultado, procedimiento=procedimiento_html)