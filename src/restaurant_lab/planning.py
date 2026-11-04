"""Fixed-recipe, deterministic prep scenarios. No writes or automatic purchasing."""
from decimal import Decimal, InvalidOperation

UNITS = {'g': ('g', Decimal(1)), 'kg': ('g', Decimal(1000)),
         'ml': ('ml', Decimal(1)), 'l': ('ml', Decimal(1000)), 'each': ('each', Decimal(1))}


def _number(value, positive=False):
    if isinstance(value, bool):
        raise ValueError('Boolean is not a quantity')
    try: number=Decimal(str(value))
    except (InvalidOperation, ValueError): raise ValueError('Use finite numeric quantities') from None
    if not number.is_finite() or number < 0 or (positive and number == 0):
        raise ValueError('Quantities must be finite and nonnegative; recipe amounts must be positive')
    if number > 1000000000 or number.as_tuple().exponent < -6:
        raise ValueError('Quantity exceeds supported size or six-decimal precision')
    return number


def _amount(record):
    unit=record['unit']
    if unit not in UNITS: raise ValueError('Unsupported unit; use g, kg, ml, l or each')
    base,scale=UNITS[unit]
    return base,_number(record['quantity'])*scale


def plan_prep(demand, recipes, inventory, capacity_minutes):
    """demand: {SKU: whole portions}; recipes: {SKU:{ingredients:{name:{quantity,unit}},minutes}}.

    Inventory uses the same ingredient records. No mass/volume or ingredient substitutions.
    Alphabetical SKU allocation is transparent, not an optimization/profit claim.
    Returns full-demand shortages plus a feasible whole-portion allocation and leftovers.
    """
    capacity=_number(capacity_minutes)
    stock={name:_amount(record) for name,record in inventory.items()}
    normalized={}; required={}
    for sku,count in demand.items():
        if not isinstance(sku,str) or not sku or type(count) is not int or not 0 <= count <= 100000:
            raise ValueError('Demand must map nonempty SKUs to bounded nonnegative whole portions')
        if sku not in recipes: raise ValueError(f'Missing fixed recipe for {sku}')
        recipe=recipes[sku];minutes=_number(recipe['minutes'],positive=True)
        if not recipe['ingredients']: raise ValueError('Recipe needs ingredients')
        ingredients={}
        for name,record in recipe['ingredients'].items():
            unit,amount=_amount(record)
            if amount <= 0: raise ValueError('Recipe amounts must be positive')
            if name not in stock: raise ValueError(f'Missing counted inventory for {name}')
            if stock[name][0] != unit: raise ValueError(f'Incompatible units for {name}')
            ingredients[name]=amount
            required[name]=required.get(name,Decimal(0))+amount*count
        normalized[sku]=(minutes,ingredients)
    remaining={name:amount for name,(_,amount) in stock.items()}
    time_left=capacity; prepared={};unmet={}
    for sku in sorted(demand):
        minutes,ingredients=normalized[sku]
        feasible=min([demand[sku],int(time_left//minutes)]+[int(remaining[n]//q) for n,q in ingredients.items()])
        prepared[sku]=feasible;unmet[sku]=demand[sku]-feasible
        time_left-=minutes*feasible
        for name,amount in ingredients.items():remaining[name]-=amount*feasible
    full_minutes=sum((normalized[sku][0]*count for sku,count in demand.items()),Decimal(0))
    return dict(policy='Alphabetical SKU order, whole portions, fixed recipes; scenario only',
        requested=dict(demand),prepared=prepared,unmet=unmet,
        ingredients=[dict(ingredient=n,unit=stock[n][0],required=str(q),available=str(stock[n][1]),
            shortage=str(max(Decimal(0),q-stock[n][1])),remaining_after_prep=str(remaining[n])) for n,q in sorted(required.items())],
        minutes_required=str(full_minutes),minutes_available=str(capacity),minutes_used=str(capacity-time_left),
        minutes_shortfall=str(max(Decimal(0),full_minutes-capacity)))
