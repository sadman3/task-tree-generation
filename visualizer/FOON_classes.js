class Thing {
	constructor(n, l) {
		this.identifier = n; this.label = l;
	}

	setLabel(S) {
		this.label = S;
	}

	getLabel() {
		return this.label;
	}

	getType() {
		return this.identifier;
	}

	setType(T) {
		this.identifier = T;
	}

	equals(T) {
		return T.getType() === this.getType();
	}
}

class ObjectNode {

	// -- constructor method for an Object object (lol)
	constructor(N, M) {
		this.setObjectType(N);
		this.setObjectLabel(M);
		this.objectStates = [];
		this.objectIngredients = [];
		this.print_functions = [this.printObject_lvl1, this.printObject_lvl2, this.printObject_lvl3];
		this.equals_functions = [this.equals_lvl1, this.equals_lvl2, this.equals_lvl3];
	}

	getObjectType() {
		return this.objectType;
	}

	setObjectType(N) {
		this.objectType = N;
	}

	getObjectLabel() {
		return this.objectLabel;
	}

	setObjectLabel(L) {
		this.objectLabel = L;
	}

	// NOTE: objects can have multiple states, so we are working with a list of states:
	getStatesList() {
		return this.objectStates;
	}

	setStatesList(S) {
		this.objectStates = S; this.objectStates.sort();
	}

	addStateType(S) {
		this.objectStates.push(S); this.objectStates.sort();
	}

	getStateType(X) {
		return this.objectStates[X][0];
	}

	getStateLabel(X) {
		return this.objectStates[X][1];
	}

	getStateRelater(X) {
		return this.objectStates[X][2];
	}

	getIngredients(X) {
		return this.objectIngredients;
	}

	setIngredients(L, X) {
		this.objectIngredients = Array(L);
	}

	addIngredient(X) {
		this.objectIngredients.push(X);
	}

	getIngredientsText() {
		var ingredients = "";
		ingredients_list = this.getIngredients(X);
		if (ingredients_list == null)
			return ingredients;
		ingredients += "{";
		for (var x = 0; x < ingredients_list.length; x++) {
			ingredients += ingredients_list[x];
			if (x < ingredients_list.length - 1)
				ingredients += ",";
		}
		ingredients += "}";
		return ingredients;
	}

	getObjectText() {
		var text = "O" + str(this.getType()) + "\t" + this.getLabel();
		for (var x = 0; x < this.objectStates.length; x++) {
			text += "\nS" + str(this.getStateType(x)) + "\t" + this.getStateLabel(x) + "\t" + this.getIngredientsText(x);
		}
		return text;
	}

	printObject_lvl1() {
		console.log("O" + this.getType() + "\t" + this.getLabel());
	}

	printObject_lvl2() {
		console.log("O" + (this.getType()) + "\t" + (this.getLabel()));
		for (var x = 0; x < this.objectStates.length; x++) {
			console.log("S" + this.getStateType(x) + "\t" + this.getStateLabel(x)
				+ (this.getSelfRelater(x) == null ? String("\t" + "[" + this.getSelfRelater(x) + "]") : '' ));
		}
	}

	printObject_lvl3() {
		console.log("O" + (this.getType()) + "\t" + (this.getLabel()));
		for (var x = 0; x < this.objectStates.length; x++) {
			if (this.getStateLabel(x) === "contains")
				console.log("S" + this.getStateType(x) + "\t" + this.getStateLabel(x) + "\t" + this.getIngredientsText(x));
			else 
				console.log("S" + this.getStateType(x) + "\t" + this.getStateLabel(x) 
					+ (this.getSelfRelater(x) == null ? String("\t" + "[" + this.getSelfRelater(x) + "]") : '' ));
		}
	}

	isSameStates(O) {
		var count = 0;
		O.objectStates.sort(); this.objectStates.sort();
		if (this.objectStates.length !== O.objectStates.length){
			return false;
		}
		for (var S = 0; S < this.objectStates.length; S++) {
			if (this.getStateType(S) === O.getStateType(S) && this.getStateLabel(S) === O.getStateLabel(S)) {
				count++;
			}
			if (this.getStateRelater(S) != null && O.getStateRelater(S) != null){
				if (this.getStateRelater(S) != O.getStateRelater(S))
					count--;
			}
		}
		if (count === O.objectStates.length){
			return true;
		}
		return false;
	}

	isSameIngredients(O) {
		if (this.getIngredients().length === O.getIngredients().length){
			for (var j = 0; j < this.getIngredients().length; j++){
				if (this.getIngredients()[j] !== O.getIngredients()[j]){ 
					return false;
				}
			}
		} else {
			return false;
		}
		return true;
	}

	equals_lvl1(O) {
		return this.getObjectType() === O.getObjectType();
	}

	equals_lvl2(O) {
		return this.equals_lvl1(O) && this.isSameStates(O);
	}

	equals_lvl3(O) {
		return this.equals_lvl2(O) && this.isSameIngredients(O);
	}
}

class MotionNode {

	constructor(N, L) {
		this.setMotionType(N);
		this.setLabel(L);
	}

	setLabel(L) {
		this.motionLabel = L;
	}

	getMotionType() {
		return this.motionType;
	}

	getLabel() {
		return this.motionLabel;
	}

	printMotion() {
		console.log("M" + this.getMotionType() + "\t" + this.getLabel());
	}

	equals(M) {
		return M.getMotionType() === this.getMotionType();
	}

	getMotion() {
		var text = "M" + this.getMotionType() + "\t" + this.getMotionLabel();
		return text;
	}

	setMotionType(T) {
		this.motionType = T;
	}
}

class FunctionalUnit {

	constructor() {
		this.inputNodes = [];
		this.outputNodes = [];
		this.inDescriptor = [];
		this.outDescriptor = [];
		this.motionNode = new MotionNode();
		this.times = ["", ""];
		this.indication = [];
		this.success_rate = -1.0;
		this.equals_functions = [this.equals_lvl1, this.equals_lvl2, this.equals_lvl3];
		this.print_functions = [this.printFunctionalUnit_lvl1, this.printFunctionalUnit_lvl2, this.printFunctionalUnit_lvl3];
	}

	addObjectNode(O, N, D) {
		if (N == 1) {
			this.inputNodes.push(O);
			this.inDescriptor.push(D);
		} else if (N == 2) {
			this.outputNodes.push(O);
			this.outDescriptor.push(D);
		} else { }
	}

	equals_lvl1(U) {
		var results = 0; // this number must add up to three (3) which suggests that all parts match!
		var count = 0; // counter used to determine number of hits (true matches)
		// checking if the input nodes are all the same!
		for (var T = 0; T < this.inputNodes.length; T++) {
			for (var TU = 0; TU < U.inputNodes.length; TU++) {
				if (this.inputNodes[T].equals_lvl1(U.inputNodes[TU])) {
					count++;
				}
			}
		}
		// if the counter matches up to the number of inputs,
		//	then that means we have the same set of inputs.
		if (count === this.getNumberOfInputs() && this.getNumberOfInputs() === U.getNumberOfInputs()) {
			results++;
		}

		// checking if the Motion is the same
		if (this.motionNode.equals(U.motionNode)) {
			results++;
		}

		// checking if the output nodes are all the same!
		count = 0;
		for (var T = 0; T < this.outputNodes.length; T++) {
			for (var TU = 0; TU < U.outputNodes.length; TU++) {
				if (this.outputNodes[T].equals_lvl1(U.outputNodes[TU])) {
					count++;
				}
			}
		}
		if (count === this.getNumberOfOutputs() && this.getNumberOfOutputs() === U.getNumberOfOutputs()) {
			results++;
		}

		// simply return true or false depending on the value of results
		return (results === 3);
	}

	equals_lvl2(U) {
		var results = 0; // this number must add up to three (3) which suggests that all parts match!
		var count = 0; // counter used to determine number of hits (true matches)
		// checking if the input nodes are all the same!
		for (var T = 0; T < this.inputNodes.length; T++) {
			for (var TU = 0; TU < U.inputNodes.length; TU++) {
				if (this.inputNodes[T].equals_lvl2(U.inputNodes[TU])) {
					count++;
				}
			}
		}
		// if the counter matches up to the number of inputs,
		//	then that means we have the same set of inputs.
		if (count === this.getNumberOfInputs() && this.getNumberOfInputs() === U.getNumberOfInputs()) {
			results++;
		}

		// checking if the Motion is the same
		if ((this.motionNode).equals(U.motionNode)) {
			results++;
		}

		// checking if the output nodes are all the same!
		count = 0;
		for (var T = 0; T < this.outputNodes.length; T++) {
			for (var TU = 0; TU < U.outputNodes.length; TU++) {
				if (this.outputNodes[T].equals_lvl2(U.outputNodes[TU])) {
					count++;
				}
			}
		}
		if (count === this.getNumberOfOutputs() && this.getNumberOfOutputs() === U.getNumberOfOutputs()) {
			results++;
		}

		// simply return true or false depending on the value of results
		return (results === 3);
	}

	equals_lvl3(U) {
		var results = 0; // this number must add up to three (3) which suggests that all parts match!
		var count = 0; // counter used to determine number of hits (true matches)
		// checking if the input nodes are all the same!
		for (var T = 0; T < this.inputNodes.length; T++) {
			for (var TU = 0; TU < U.inputNodes.length; TU++) {
				if (this.inputNodes[T].equals_lvl3(U.inputNodes[TU])) {
					count++;
				}
			}
		}
		// if the counter matches up to the number of inputs,
		//	then that means we have the same set of inputs.
		if (count === this.getNumberOfInputs() && this.getNumberOfInputs() === U.getNumberOfInputs()) {
			results++;
		}

		// checking if the Motion is the same
		if ((this.motionNode).equals(U.motionNode)) {
			results++;
		}

		// checking if the output nodes are all the same!
		count = 0;
		for (var T = 0; T < this.outputNodes.length; T++) {
			for (var TU = 0; TU < U.outputNodes.length; TU++) {
				if (this.outputNodes[T].equals_lvl3(U.outputNodes[TU])) {
					count++;
				}
			}
		}
		if (count === this.getNumberOfOutputs() && this.getNumberOfOutputs() === U.getNumberOfOutputs()) {
			results++;
		}

		// simply return true or false depending on the value of results
		return (results === 3);
	}

	getMotionNode() {
		return this.motionNode;
	}

	getInputList() {
		return this.inputNodes;
	}

	getOutputList() {
		return this.outputNodes;
	}

	setMotionNode(M) {
		this.motionNode = M;
	}

	setInputList(L) {
		this.inputNodes = L;
	}

	setOutputList(L) {
		this.outputNodes = L;
	}

	getNumberOfInputs() {
		return this.inputNodes.length;
	}

	getNumberOfOutputs() {
		return this.outputNodes.length;
	}

	setTimes(S, E) {
		this.times[0] = S; this.times[1] = E;
	}

	getStartTime() {
		return this.times[0];
	}

	getEndTime() {
		return this.times[1];
	}

	getSuccessRate() {
		return this.success_rate;
	}

	setSuccessRate(SR) {
		this.success_rate = SR;
	}

	getIndication() {
		return this.indication;
	}

	setIndication(I) {
		this.indication = I;
	}

	printFunctionalUnit_lvl1() {
		var count = 0;
		for (T in this.inputNodes) {
			console.log("O" + T.getObjectType() + "\t" + T.getObjectLabel() + "\t" + this.inDescriptor[count]);
			count++;
		}
		console.log(this.motionNode.getMotion() + "\t" + this.times[0] + "\t" + this.times[1]);
		count = 0;
		for (T in this.outputNodes) {
			console.log("O" + T.getObjectType() + "\t" + T.getObjectLabel() + "\t" + this.outDescriptor[count]);
			count++;
		}
		if (this.success_rate > -1.0)
			console.log("success rate for Robot: " + this.success_rate);
	}

	printFunctionalUnit_lvl2() {
		var count = 0;
		for (T in this.inputNodes) {
			console.log("O" + T.getObjectType() + "\t" + T.getObjectLabel() + "\t" + this.inDescriptor[count]);
			for (var x = 0; x < T.getStatesList().length; x++) {
				console.log("S" + T.getStateType(x) + "\t" + T.getStateLabel(x));
			}
			count++;
		}
		console.log(this.motionNode.getMotion() + "\t" + this.times[0] + "\t" + this.times[1]);
		count = 0;
		for (T in this.outputNodes) {
			console.log("O" + T.getObjectType() + "\t" + T.getObjectLabel() + "\t" + this.outDescriptor[count]);
			for (var x = 0; x < T.getStatesList().length; x++) {
				console.log("S" + T.getStateType(x) + "\t" + T.getStateLabel(x) + (this.getSelfRelater(x) == null ? String("\t" + "[" + this.getSelfRelater(x) + "]") : '' ));
			}
			count++;
		}
		if (this.success_rate > -1.0)
			console.log("success rate for Robot: " + this.success_rate);
	}

	printFunctionalUnit_lvl3() {
		var count = 0;
		for (T in this.inputNodes) {
			console.log("O" + T.getObjectType() + "\t" + T.getObjectLabel() + "\t" + this.inDescriptor[count]);
			for (var x = 0; x < T.getStatesList().length; x++) {
				if (T.getStateLabel(x) == "contains") console.log("S" + T.getStateType(x) + "\t" + T.getStateLabel(x) + "\t" + T.getIngredientsText(x));
				else console.log("S" + T.getStateType(x) + "\t" + T.getStateLabel(x) + (this.getSelfRelater(x) == null ? String("\t" + "[" + this.getSelfRelater(x) + "]") : '' ));
			}
			count = count++;
		}
		console.log(this.motionNode.getMotion() + "\t" + this.times[0] + "\t" + this.times[1]);
		count = 0;
		for (T in this.outputNodes) {
			console.log("O" + T.getObjectType() + "\t" + T.getObjectLabel() + "\t" + this.outDescriptor[count]);
			for (var x = 0; x < T.getStatesList().length; x++) {
				if (T.getStateLabel(x) == "contains") console.log("S" + T.getStateType(x) + "\t" + T.getStateLabel(x) + "\t" + T.getIngredientsText(x));
				else console.log("S" + T.getStateType(x) + "\t" + T.getStateLabel(x) + (this.getSelfRelater(x) == null ? String("\t" + "[" + this.getSelfRelater(x) + "]") : '' ));
			}
			count++;
		}
		if (this.success_rate > -1.0)
			console.log("success rate for Robot: " + this.success_rate);
	}
}
